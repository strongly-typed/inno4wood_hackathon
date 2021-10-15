from dataclasses import dataclass
from typing import Optional
from lxml import etree
from pathlib import Path

from xsdata.formats.dataclass.parsers import XmlParser

from btlx.btlx_11 import Btlx, CoordinateType, field
from btlx.btlx_11 import ArcType, LineType, MillContourType

@dataclass
class LineSegmentType:
    """
    Definition of a segment, either from LineType.
    """
    start_point: Optional[CoordinateType] = field(
        default=None,
        metadata={
            "name": "StartPoint",
            "type": "Element",
            "required": True,
        }
    )
    end_point: Optional[float] = field(
        default=None,
        metadata={
            "name": "EndPoint",
            "type": "Attribute",
            "required": True,
        }
    )
    inclination: Optional[float] = field(
        default=None,
        metadata={
            "name": "Inclination",
            "type": "Attribute",
            "min_inclusive": -89.9,
            "max_inclusive": 89.9,
        }
    )

    # point_on_arc could be added for ArcType. None = Line, not None = Arc?

segment = LineSegmentType()
segment.start_point = CoordinateType(x=1620.74, y=1073.13, z=0.0)
segment.end_point = CoordinateType(x=1964.64, y=1073.13, z=0.0)
segment.inclination = 0.0

def process_contour(choice: MillContourType) -> None:
    print(f' - {choice.name=}')
    print(f' - {choice.reference_plane_id=}')

    print(f' - {choice.contour.start_point=}')

    last_point = choice.contour.start_point

    segments = []

    for loa in choice.contour.line_or_arc or []:
        if isinstance(loa, LineType) and not isinstance(loa, ArcType):
            # print(f'   - {loa}')
            segments.append(LineSegmentType(
                start_point=last_point,
                end_point=loa.end_point,
                inclination=loa.inclination))
            last_point = loa.end_point
        elif isinstance(loa, LineType) and isinstance(loa, ArcType):
            # ArcType is a subclass of LineType
            # print(f'   o {loa}')
            # skip arc
            last_point = loa.end_point
        else:
            print(f'   x {loa}')

    for segment in segments:
        print(segment)



# https://design2machine.com/btlx/BTLx_2_0_0.xsd
# filename_xsd = '10_BTLx/BTLx_2_0_0.xsd'
filename_xsd = '10_BTLx/btlx_11.xsd'
xmlschema_doc = etree.parse(filename_xsd)
xmlschema = etree.XMLSchema(xmlschema_doc)

# path = 'tests/50.1662.100_IW_Transport_06.btlx'
path = '10_BTLx/input.btlx'

with open(path, 'r') as xml_file:
    btlx_str = xml_file.read()

    try:
        btlx_bytes = bytes(bytearray(btlx_str, encoding='utf-8'))
        doc = etree.fromstring(btlx_bytes)

    except IOError:
        print(f'❌ {path} Invalid File')

    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        print(f'❌ {path} XML Syntax Error, see error_syntax.log')
        with open(path.stem + '-error_syntax.log', 'w') as error_log_file:
            error_log_file.write(str(err.error_log))

    except:
        print(f'❌ {path} Unknown error, exiting.')
        quit()

    # Validate
    try:
        # xmlschema.assertValid(doc)
        print(f'✅ {path}')

    except etree.DocumentInvalid as err:
        print(f'❌ {path} Schema validation error, see error_schema.log')


    # load BLTx
    parser = XmlParser()
    btlx = parser.from_bytes(btlx_bytes, Btlx)

    for part in btlx.project.parts.part:
        print(f'{part.designation=}')
        for transformation in part.transformations.transformation:
            print(f'{transformation.position.reference_point.x=}')
            print(f'{transformation.position.reference_point.y=}')
            print(f'{transformation.position.reference_point.z=}')
            print(f'{transformation.position.xvector.x=}')
            print(f'{transformation.position.xvector.y=}')
            print('')
