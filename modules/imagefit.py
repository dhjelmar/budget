def imagefit(pdf, image, wpdf, y, max_y, margin_top, extra=0, atleast=0):
    '''
    add page to pdf object if there is insufficient room for image

    Input
    -----
    pdf   = pdf object
    image = image file
    wpdf  = width of image file in pdf units
    y     = current y location on page
    extra = additional height to require beyond image height
    atleast = minimum height to require regardless of image height

    Output
    ------
    current y value (only different from input if new page is added)
    '''
    from PIL import Image

    ## figure out height of image in pdf units
    img_heightp = Image.open(image).height    # image height in pixels
    img_widthp  = Image.open(image).width     # image width in pixels
    img_height  = wpdf * img_heightp / img_widthp            # image height in pdf units

    max_y_needed = y + max(img_height + extra, atleast)

    if max_y_needed > max_y:
        pdf.add_page()
        print('added new page to fit image', image)
        print('max_y_needed =', max_y_needed, '> max_y =', max_y)
        print('resetting current_y to top of page')
        y = margin_top
        pdf.set_y(y)

    return y
