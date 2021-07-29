from unittest import TestCase
from bs4 import BeautifulSoup

from information_extraction.InformationExtraction import InformationExtraction
from segments_boxes.SegmentsBoxes import SegmentsBoxes, SegmentBox


class TestDocument(TestCase):
    def test_from_information_extraction(self):
        xml_string = '<?xml version="1.0" encoding="utf-8"?>\
                        <alto ><Description><MeasurementUnit>pixel</MeasurementUnit><sourceImageInformation><fileName>\
                        <Styles>\
                            <TextStyle FONTCOLOR="000000" FONTFAMILY="glyphlessfont" FONTSIZE="11.000" FONTTYPE="sans-serif" FONTWIDTH="fixed" ID="font0"/>\
                        </Styles>\
                        <Page HEIGHT="1" ID="Page1" PHYSICAL_IMG_NR="1" WIDTH="2">\
                            <TextLine HEIGHT="1" HPOS="2" ID="p1_t1" VPOS="3" WIDTH="4">\
                            <String CONTENT="first" HEIGHT="1" HPOS="2" ID="p1_w1" STYLEREFS="font0" VPOS="3" WIDTH="4"/>\
                            </TextLine>\
                        </Page>\
                        <Page HEIGHT="3" ID="Page2" PHYSICAL_IMG_NR="2" WIDTH="4">\
                            <TextLine HEIGHT="4" HPOS="3" ID="p2_t1" VPOS="2" WIDTH="1">\
                            <String CONTENT="second" HEIGHT="4" HPOS="3" ID="p2_w1" STYLEREFS="font0" VPOS="2" WIDTH="1"/>\
                            </TextLine>\
                        </Page>\
                        </alto>'

        tags = BeautifulSoup(xml_string, "lxml-xml")

        information_extraction = InformationExtraction(tags)
        segments_boxes = SegmentsBoxes.from_information_extraction(information_extraction)

        self.assertEqual(segments_boxes.page_width, 2)
        self.assertEqual(segments_boxes.page_height, 1)

        self.assertEqual(segments_boxes.segment_boxes[0].left, 2)
        self.assertEqual(segments_boxes.segment_boxes[0].top, 3)
        self.assertEqual(segments_boxes.segment_boxes[0].width, 4)
        self.assertEqual(segments_boxes.segment_boxes[0].height, 1)
        self.assertEqual(segments_boxes.segment_boxes[0].page_number, 1)

        self.assertEqual(segments_boxes.segment_boxes[1].left, 3)
        self.assertEqual(segments_boxes.segment_boxes[1].top, 2)
        self.assertEqual(segments_boxes.segment_boxes[1].width, 1)
        self.assertEqual(segments_boxes.segment_boxes[1].height, 4)
        self.assertEqual(segments_boxes.segment_boxes[1].page_number, 2)

    def test_to_json(self):
        segments_boxes = SegmentsBoxes(1, 2, [SegmentBox(1, 2, 3, 4, 1), SegmentBox(0.1, 0.2, 0.3, 0.4, 2)])
        json_result = '{"pageWidth": 1, "pageHeight": 2, "segments": [' \
                      '{"left": 1, "top": 2, "width": 3, "height": 4, "pageNumber": 1}, ' \
                      '{"left": 0.1, "top": 0.2, "width": 0.3, "height": 0.4, "pageNumber": 2}]}'
        self.assertEqual(segments_boxes.to_json(), json_result)
