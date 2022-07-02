from PIL import Image
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile


def resized_image_value(source, width, height):
    box_width, box_height = (width, height)
    box_ratio = box_width / box_height
    image = Image.open(source)
    image_width, image_height = (image.width, image.height)
    image_ratio = image_width / image_height
    if image_ratio == box_ratio:
        processed_image = image.resize((box_width, box_height), Image.BILINEAR)
    else:
        if image_width >= image_height:
            # 너비가 긴 이미지
            # 이미지 높이를 박스 높이에 맞춰서 rescale
            resized_width = int(box_height * image_ratio)
            if resized_width < box_width:
                resized_height = int(box_width / image_ratio)
                resized_image = image.resize((resized_width, resized_height), Image.BILINEAR)
            else:
                resized_image = image.resize((resized_width, box_height), Image.BILINEAR)
        else:
            # 높이가 큰 이미지
            # 이미지 너비를 박스 너비에 맞춰서 rescale
            resized_height = int(box_width / image_ratio)
            if resized_height < box_height:
                resized_width = int(box_height * image_ratio)
                resized_image = image.resize((resized_width, resized_height), Image.BILINEAR)
            else:
                resized_image = image.resize((box_width, resized_height), Image.BILINEAR)
        resized_width, resized_height = resized_image.size
        center_x, center_y = (int(resized_width / 2), int(resized_height / 2))
        half_box_width, half_box_height = (int(box_width / 2), int(box_height / 2))

        left = int(center_x - half_box_width)
        top = int(center_y - half_box_height)
        right = int(center_x + half_box_width)
        bottom = int(center_y + half_box_height)

        processed_image = resized_image.crop((left, top, right, bottom))

    result_image = processed_image.convert('RGB')
    image_io = BytesIO()
    result_image.save(image_io, 'JPEG', optimize=True, progressive=True, quality=100)
    content_type = source.content_type
    charset = source.charset
    process_value = InMemoryUploadedFile(name='img.jpeg', content_type=content_type, size=(box_width, box_height), charset=charset, field_name='image', file=image_io)

    return process_value
