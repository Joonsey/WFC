from PIL import Image
ASSET_PATH = "tiles/"

tile_size = 8
def split_sheets(path) -> None:
    with Image.open(path) as im:
        columns = im.width // tile_size
        for column in range(columns):
            x_offset = column*tile_size
            cropped_image_name = ASSET_PATH+str(1+column)+".png"
            im.crop((x_offset, 0, x_offset + tile_size, 0+tile_size)).save(cropped_image_name, 'png')


split_sheets("tiles/Sprite-0001.png")
