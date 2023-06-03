def rmdir(folder):
    '''
    if folder exists, remove folder and contents

    from:
    https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
    '''
    import os

    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))

            # Add this block to remove folders
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

        # Add this line to remove the root folder at the end
        os.rmdir(folder)

## path = 'figures/'
## rmdir(path)
