from tabulate import tabulate

from PredictionInfo import PredictionInfo
from paragraph_extraction_trainer.PdfParagraphTokens import PdfParagraphTokens


class BenchmarkTable:
    def __init__(self, pdf_paragraph_tokens_list: list[PdfParagraphTokens], total_time: float):
        self.pdf_paragraphs_tokens_list: list[PdfParagraphTokens] = pdf_paragraph_tokens_list
        self.total_time = total_time
        self.prediction_info_list = [PredictionInfo(paragraph_tokens) for paragraph_tokens in pdf_paragraph_tokens_list]

    @staticmethod
    def get_mistakes_for_file(predictions_for_file: PredictionInfo):
        labels_for_file = 0
        mistakes_for_file = 0
        for page in predictions_for_file.pdf_paragraph_tokens.pdf_features.pages:
            actual_coordinates = predictions_for_file.actual_paragraph_coordinates_by_page[page]
            predicted_coordinates = predictions_for_file.predicted_paragraph_coordinates_by_page[page]
            actual_coordinates_set = {tuple(coordinate.to_dict().values()) for coordinate in actual_coordinates}
            predicted_coordinates_set = {tuple(coordinate.to_dict().values()) for coordinate in predicted_coordinates}
            labels_for_file += len(actual_coordinates)
            mistakes_for_file += len(set(actual_coordinates_set) - set(predicted_coordinates_set))
        return labels_for_file, mistakes_for_file

    def get_mistakes_for_file_type(self, predictions_for_file_type: list[PredictionInfo]):
        labels_for_file_type = 0
        mistakes_for_file_type = 0
        for predictions_for_file in predictions_for_file_type:
            labels_for_file, mistakes_for_file = self.get_mistakes_for_file(predictions_for_file)
            labels_for_file_type += labels_for_file
            mistakes_for_file_type += mistakes_for_file
        return labels_for_file_type, mistakes_for_file_type

    def get_benchmark_table_rows(self):
        benchmark_table_rows: list[list[str]] = []
        file_types = set(info.file_type for info in self.prediction_info_list)
        total_label_count = 0
        total_mistake_count = 0
        for file_type in file_types:
            predictions_for_file_type = [info for info in self.prediction_info_list if info.file_type == file_type]
            labels_for_file_type, mistakes_for_file_type = self.get_mistakes_for_file_type(predictions_for_file_type)
            total_label_count += labels_for_file_type
            total_mistake_count += mistakes_for_file_type
            accuracy = round(100 - (100 * mistakes_for_file_type / labels_for_file_type), 2)
            benchmark_table_rows.append([file_type, f"{mistakes_for_file_type}/{labels_for_file_type} ({accuracy}%)"])

        return benchmark_table_rows, total_label_count, total_mistake_count

    def prepare_benchmark_table(self):
        table_headers = ["File Type", "Mistakes"]
        table_rows, total_label_count, total_mistake_count = self.get_benchmark_table_rows()
        average_accuracy = 100 - (100 * total_mistake_count / total_label_count)
        with open("benchmark_table.txt", "w") as benchmark_file:
            benchmark_table = (
                tabulate(tabular_data=table_rows, headers=table_headers)
                + "\n\n"
                + f"Average Accuracy: {total_mistake_count}/{total_label_count} ({round(average_accuracy, 2)}%)"
                + "\n"
                + f"Total Time: {round(self.total_time, 2)}"
            )
            benchmark_file.write(benchmark_table)
