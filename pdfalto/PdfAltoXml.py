import os
import pickle
import shutil
import subprocess
import pathlib
import platform
import uuid
from collections import namedtuple
from typing import List, Dict, Tuple

import nltk as nltk
import numpy as np

from bs4 import BeautifulSoup, Tag

from pdfalto.PDFFeatures import PDFFeatures
from pdfalto.get_tags_by_page_pdfalto import get_tags_by_page_pdfalto
from information_extraction.reading_order import get_tuples_pdfalto_reading_order_next

SegmentPdfalto = namedtuple('SegmentPdfalto', ['page_number', 'page_width', 'page_height', 'xml_tags'])

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()

MODEL = pickle.load(open(f'{THIS_SCRIPT_PATH}/segmentation_model.pkl', 'rb'))


class PdfAltoXml:
    ML_CLASS_LABEL_PROPERTY = 'MLCLASSLABEL'

    def __init__(self, xml_file: BeautifulSoup):
        self.xml_file = xml_file
        self.tags_by_page = get_tags_by_page_pdfalto(self.xml_file)
        self.pdf_features = PDFFeatures(self.tags_by_page)
        self.fonts = list(self.tags_by_page.keys())[0].fonts

    def get_segments(self) -> (Dict[int, List[Tag]], Dict[int, List[Tag]]):
        segments_pdfalto: List[SegmentPdfalto] = list()

        for page_info, tags in self.tags_by_page.items():
            X = self.get_training_data_one_page(tags)
            if X is None:
                if len(tags) == 1:
                    segment_pdfalto = SegmentPdfalto(page_info.page_number, page_info.width, page_info.height,
                                                     [tags[0]])
                    segments_pdfalto.append(segment_pdfalto)
                continue

            y = MODEL.predict(X) if len(X.shape) == 2 else MODEL.predict([X])
            same_paragraph_prediction = [True if prediction > 0.5 else False for prediction in y]

            segment_pdfalto = SegmentPdfalto(page_info.page_number, page_info.width, page_info.height, [tags[0]])
            segments_pdfalto.append(segment_pdfalto)
            for prediction_index, same_paragraph in enumerate(same_paragraph_prediction):
                if same_paragraph:
                    segments_pdfalto[-1].xml_tags.append(tags[prediction_index + 1])
                    continue

                segment_pdfalto = SegmentPdfalto(page_info.page_number,
                                                 page_info.width,
                                                 page_info.height,
                                                 [tags[prediction_index + 1]])

                segments_pdfalto.append(segment_pdfalto)

        return segments_pdfalto, self.fonts, self.pdf_features

    def get_one_tag_segments(self) -> (Dict[int, List[Tag]], Dict[int, List[Tag]]):
        segments_pdfalto: List[SegmentPdfalto] = list()

        for page_info, tags in self.tags_by_page.items():
            for tag in tags:
                segment_pdfalto = SegmentPdfalto(page_info.page_number, page_info.width, page_info.height, [tag])
                segments_pdfalto.append(segment_pdfalto)

        return segments_pdfalto, self.fonts, self.pdf_features

    def get_features(self, tag_tuples_to_check, tags):
        X = None

        for tag_tuple in tag_tuples_to_check:
            tag_1 = tag_tuple[0]
            tag_2 = tag_tuple[1]

            top_1 = float(tag_1['VPOS'])
            height_1 = float(tag_1['HEIGHT'])
            left_1 = float(tag_1['HPOS'])
            width_1 = float(tag_1['WIDTH'])
            right_1 = self.pdf_features.page_width - width_1 - left_1

            on_the_right_left_1, on_the_right_right_1 = self.get_on_the_right_block(tag_1, tags)
            on_the_left_left_1, on_the_left_right_1 = self.get_on_the_left_block(tag_1, tags)

            right_gap_1 = on_the_right_left_1 - right_1
            left_gap_1 = left_1 - on_the_left_right_1

            top_2 = float(tag_2['VPOS'])
            height_2 = float(tag_2['HEIGHT'])
            left_2 = float(tag_2['HPOS'])
            width_2 = float(tag_2['WIDTH'])
            right_2 = self.pdf_features.page_width - width_2 - left_2

            on_the_right_left_2, on_the_right_right_2 = self.get_on_the_right_block(tag_2, tags)
            on_the_left_left_2, on_the_left_right_2 = self.get_on_the_left_block(tag_2, tags)

            right_gap_2 = on_the_right_left_2 - right_2
            left_gap_2 = left_2 - on_the_left_right_2

            absolute_right_1 = max(left_1 + width_1, on_the_right_right_1)
            absolute_right_2 = max(left_2 + width_2, on_the_right_right_2)

            end_lines_difference = abs(absolute_right_1 - absolute_right_2)

            on_the_left_left_1 = left_1 if on_the_left_left_1 == 0 else on_the_left_left_1
            on_the_left_left_2 = left_2 if on_the_left_left_2 == 0 else on_the_left_left_2
            absolute_left_1 = min(left_1, on_the_left_left_1)
            absolute_left_2 = min(left_2, on_the_left_left_2)

            start_lines_differences = absolute_left_1 - absolute_left_2

            tags_in_the_middle = list(filter(lambda x: (top_1 + height_1) <= float(x['VPOS']) < top_2, tags))
            tags_in_the_middle_right = min(
                map(lambda x: float(x['HPOS']) + float(x['WIDTH']), tags_in_the_middle)) if len(
                tags_in_the_middle) > 0 else 0
            tags_in_the_middle_top = max(map(lambda x: float(x['VPOS']), tags_in_the_middle)) if len(
                tags_in_the_middle) > 0 else 0
            tags_in_the_middle_bottom = min(
                map(lambda x: float(x['VPOS']) + float(x['HEIGHT']), tags_in_the_middle)) if len(
                tags_in_the_middle) > 0 else 0

            in_the_middle_top = tags_in_the_middle_top - top_1 - height_1 if tags_in_the_middle_top > 0 else 0
            in_the_middle_bottom = tags_in_the_middle_bottom - top_1 - height_1 if tags_in_the_middle_bottom > 0 else 0

            tags_in_the_middle_height = tags_in_the_middle_bottom - tags_in_the_middle_top

            top_distance = top_2 - top_1 - height_1

            gap_middle_top = tags_in_the_middle_top - top_1 - height_1 if tags_in_the_middle_top > 0 else 0
            gap_middle_bottom = top_2 - tags_in_the_middle_bottom if tags_in_the_middle_bottom > 0 else 0

            top_distance_gaps = top_distance - (gap_middle_bottom - gap_middle_top)

            right_distance = left_2 - left_1 - width_1
            left_distance = left_1 - left_2

            bottom_tags_list = list(filter(lambda x: (top_2 + height_2) < float(x['VPOS']), tags))

            bottom_space = max(map(lambda x: float(x['VPOS']), bottom_tags_list)) - (top_2 + height_2) if len(
                bottom_tags_list) > 0 else 0

            height_difference = height_1 - height_2

            strings_tags_1 = ' '.join(map(lambda x: x['CONTENT'], tag_1.find_all('String')))
            strings_tags_2 = ' '.join(map(lambda x: x['CONTENT'], tag_2.find_all('String')))

            tokens_options = ['LS', 'TO', 'VBN', "''", 'WP', 'UH', 'VBG', 'JJ', 'VBZ', '--', 'VBP', 'NN', 'DT', 'PRP',
                              ':',
                              'WP$', 'NNPS', 'PRP$', 'WDT', '(', ')', '.', ',', '``', '$', 'RB', 'RBR', 'RBS', 'VBD',
                              'IN',
                              'FW', 'RP', 'JJR', 'JJS', 'PDT', 'MD', 'VB', 'WRB', 'NNP', 'EX', 'NNS', 'SYM', 'CC', 'CD',
                              'POS', '#']

            text_1 = nltk.word_tokenize(strings_tags_1)
            text_2 = nltk.word_tokenize(strings_tags_2)

            try:
                pos_tags_1 = nltk.pos_tag(text_1)
                last_word = tokens_options.index(pos_tags_1[-1][1])
                previous_last_word = tokens_options.index(pos_tags_1[-2][1]) if len(pos_tags_1) > 1 else 0

                pos_tags_2 = nltk.pos_tag(text_2)
                text_2_first_word = tokens_options.index(pos_tags_2[0][1])
                second_word = tokens_options.index(pos_tags_2[1][1]) if len(pos_tags_2) > 1 else 0
            except:
                last_word = 50
                text_2_first_word = 50

            same_font = tag_1.find_all('String')[-1]['STYLEREFS'] == tag_2.find_all('String')[0]['STYLEREFS']

            features = np.array([[self.pdf_features.font_size_mode,
                                  last_word,
                                  text_2_first_word,
                                  same_font,
                                  absolute_right_1,
                                  width_1,
                                  right_2,
                                  left_2,
                                  width_2,
                                  top_distance,
                                  top_distance - self.pdf_features.lines_space_mode,
                                  top_distance_gaps,
                                  self.pdf_features.lines_space_mode - top_distance_gaps,
                                  self.pdf_features.right_space_mode - absolute_right_1,
                                  top_distance - height_1,
                                  start_lines_differences,
                                  right_distance,
                                  left_distance,
                                  right_gap_1,
                                  left_gap_2,
                                  height_difference,
                                  end_lines_difference]])

            X = features if X is None else np.concatenate((X, features), axis=0)

        return X

    def get_training_data_one_page(self, page_tags):
        X = None
        tag_tuples_to_check: List[Tuple[Tag, Tag]] = get_tuples_pdfalto_reading_order_next(page_tags)
        features = self.get_features(tag_tuples_to_check, page_tags)

        X = features if X is None else np.concatenate((X, features), axis=0)
        return X

    def get_training_data(self):
        X = None
        y = np.array([])

        for page_info, page_tags in self.tags_by_page.items():
            tag_tuples_to_check: List[Tuple[Tag, Tag]] = get_tuples_pdfalto_reading_order_next(page_tags)
            features = self.get_features(tag_tuples_to_check, page_tags)
            if features is None:
                continue
            X = features if X is None else np.concatenate((X, features), axis=0)
            for tag_tuple in tag_tuples_to_check:
                if tag_tuple[0]['GROUP'] == tag_tuple[1]['GROUP']:
                    y = np.append(y, 1)
                    continue

                y = np.append(y, 0)

        return X, y

    @staticmethod
    def get_on_the_right_block(tag, tags):
        top = float(tag['VPOS'])
        height = float(tag['HEIGHT'])
        left = float(tag['HPOS'])

        on_the_right = list(filter(
            lambda x: (top <= float(x['VPOS']) < (top + height)) or (top < (
                    float(x['VPOS']) + float(x['HEIGHT'])) <= (top + height)), tags))

        on_the_right = list(filter(lambda x: left < float(x['HPOS']), on_the_right))
        on_the_right_left = 0 if len(on_the_right) == 0 else min(map(lambda x: float(x['HPOS']), on_the_right))
        on_the_right_right = 0 if len(on_the_right) == 0 else max(
            map(lambda x: float(x['HPOS']) + float(x['WIDTH']), on_the_right))

        return on_the_right_left, on_the_right_right

    @staticmethod
    def get_on_the_left_block(tag, tags):
        top = float(tag['VPOS'])
        height = float(tag['HEIGHT'])
        right = float(tag['HPOS']) + float(tag['WIDTH'])

        on_the_left = list(filter(
            lambda x: (top <= float(x['VPOS']) < (top + height)) or (top < (
                    float(x['VPOS']) + float(x['HEIGHT'])) <= (top + height)), tags))

        on_the_left = list(filter(lambda x: (float(x['HPOS']) + float(x['WIDTH'])) < right, on_the_left))
        on_the_left_left = 0 if len(on_the_left) == 0 else min(map(lambda x: float(x['HPOS']), on_the_left))
        on_the_left_right = 0 if len(on_the_left) == 0 else max(
            map(lambda x: float(x['HPOS']) + float(x['WIDTH']), on_the_left))

        return on_the_left_left, on_the_left_right

    @staticmethod
    def get_segments_from_bytes(file_content: bytes) -> (Dict[int, List[Tag]], Dict[int, List[Tag]]):
        this_script_path = pathlib.Path(__file__).parent.absolute()

        pdf_path = f'{this_script_path}/pdf_to_convert.pdf'
        xml_path = f'{this_script_path}/converted.xml'
        xml_metadata_path = f'{this_script_path}/converted_metadata.xml'
        pdfalto_program_path = f'{this_script_path}/pdfalto'

        with open(pdf_path, "wb") as file:
            file.write(file_content)

        subprocess.run([pdfalto_program_path, '-readingOrder', pdf_path, xml_path])
        xml = BeautifulSoup(open(xml_path).read(), 'lxml-xml')

        os.remove(pdf_path)
        os.remove(xml_path)
        os.remove(xml_metadata_path)

        return PdfAltoXml(xml).get_segments()

    @staticmethod
    def create_xml_from_pdf(pdf_path, file_path_xml):
        if platform.system() == 'Darwin':
            pdfalto_executable = f'{THIS_SCRIPT_PATH}/pdfalto_macos'
        else:
            pdfalto_executable = f'{THIS_SCRIPT_PATH}/pdfalto_linux'

        print(pdf_path)
        print(file_path_xml)
        subprocess.run([pdfalto_executable, '-readingOrder', pdf_path, file_path_xml])

    @staticmethod
    def get_file_path(file_name, extension):
        if not os.path.exists(f'{THIS_SCRIPT_PATH}/../files/{extension}'):
            os.makedirs(f'{THIS_SCRIPT_PATH}/../files/{extension}')

        return f'{THIS_SCRIPT_PATH}/../files/{extension}/{file_name}.{extension}'

    @staticmethod
    def get_xml_tags_from_file_content(file_content):
        file_id = str(uuid.uuid1())

        file_path_pdf = pathlib.Path(PdfAltoXml.get_file_path(file_id, 'pdf'))
        file_path_pdf.write_bytes(file_content)

        file_path_xml = PdfAltoXml.get_file_path(file_id, 'xml')
        file_xml_metadata_path = file_path_xml.replace('.xml', '_metadata.xml')
        file_xml_data_path = file_path_xml.replace('.xml', '.xml_data')

        PdfAltoXml.create_xml_from_pdf(file_path_pdf, file_path_xml)

        with open(file_path_xml) as stream:
            xml_tags = BeautifulSoup(stream.read(), "lxml-xml")

        os.remove(file_path_pdf)
        os.remove(file_path_xml)
        os.remove(file_xml_metadata_path)
        shutil.rmtree(file_xml_data_path)

        return xml_tags

    @staticmethod
    def from_pdf_path(pdf_path: str, xml_file_path: str, failed_pdf_path: str):
        try:
            os.makedirs('/'.join(xml_file_path.split('/')[:-1]))
        except FileExistsError:
            pass

        file_xml_metadata_path = xml_file_path.replace('.xml', '_metadata.xml')
        file_xml_data_path = xml_file_path.replace('.xml', '.xml_data')

        PdfAltoXml.create_xml_from_pdf(pdf_path, xml_file_path)

        if not os.path.exists(xml_file_path):
            try:
                os.makedirs('/'.join(failed_pdf_path.split('/')[:-1]))
            except FileExistsError:
                pass
            shutil.move(pdf_path, failed_pdf_path)
            return

        with open(xml_file_path, 'r') as file:
            xml_elements = BeautifulSoup(file.read(), 'lxml-xml')

        os.remove(file_xml_metadata_path)
        shutil.rmtree(file_xml_data_path)

        return xml_elements
