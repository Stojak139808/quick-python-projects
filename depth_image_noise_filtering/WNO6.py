'''
This scripts corrects noise in the given sample depth image. For comparison opencv's inpaint is used,
although it honestly that method is excessive for this problem.
My method uses square window going through the image fixing holes, the result is a bit square-looking, but much faster
than inpaint. The speed also depends on how many filters have been used, so for fixing these in real time, worse resolution could be used
to achieve faster speeds.

It first displays original image, then cv2's inapint and at the end it shows my method.
Additionally it shows the data with a colored picture in a #d scatter graph, sadly the colored image I've got is from a different frame
and is a bit offset to the depth.
'''

import matplotlib.image as imgr
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

def inpaint():
    #cv2's inpaint method
    org_img = cv.imread('stairs_depth_Depth_Depth.png')
    mask = cv.cvtColor(org_img, cv.COLOR_RGB2GRAY)
    _, mask = cv.threshold(mask,1,255,cv.THRESH_BINARY)
    mask = cv.bitwise_not(mask)
    out = cv.inpaint(org_img, mask,3,cv.INPAINT_TELEA)

    return out.astype(np.float32)/255.

def inpaint_2(org_img, mask_size_width, mask_size_height):
    # my filter
    mask = cv.cvtColor(org_img, cv.COLOR_RGB2GRAY)
    _, mask = cv.threshold(mask,5,255,cv.THRESH_BINARY)
    mask_not = cv.bitwise_not(mask)
    height, width = org_img.shape[:2]

    while height%mask_size_height != 0:
        mask_size_height = mask_size_height + 1

    while width%mask_size_width != 0:
        mask_size_width = mask_size_width + 1
    
    fill = np.zeros((height, width,3), dtype=np.uint8)
    for x in range(0, int(height/mask_size_height)):
        for y in range(0, int(width/mask_size_width)):
            tmp_img = org_img[x * mask_size_height:(x + 1) * mask_size_height,
                              y * mask_size_width:(y + 1) * mask_size_width]

            tmp_mask = mask[x * mask_size_height:(x + 1) * mask_size_height,
                            y * mask_size_width:(y + 1) * mask_size_width]

            tmp_mask_not = mask_not[x * mask_size_height:(x + 1) * mask_size_height,
                                    y * mask_size_width:(y + 1) * mask_size_width]

            averge_color = cv.mean(tmp_img, mask = tmp_mask)

            N, M = org_img[x * mask_size_height:(x + 1) * mask_size_height,
                           y * mask_size_width:(y + 1) * mask_size_width].shape[:2]

            fill[x * mask_size_height:(x + 1) * mask_size_height,
                 y * mask_size_width:(y + 1) * mask_size_width] = np.ones((N, M, 3), dtype=np.uint8)*int(averge_color[0])

    out = cv.bitwise_and(fill, fill , mask = mask_not)
    out = cv.add(out, org_img)
    return out

def main():

    colors_img = imgr.imread('stairs_color_Color.png')
    cv.imshow("original image", colors_img)
    cv.waitKey()


    img = inpaint() #cv2 solution
    cv.imshow("CV2 inpaint", img)
    cv.waitKey()

    org_img = cv.imread('stairs_depth_Depth_Depth.png')
    img = org_img
    for fill_size in [2,4,6,10,20, 50, 100, 150]:
        img = inpaint_2(img, fill_size, fill_size)
    img = cv.medianBlur(img, 5)

    cv.imshow("uzupelniona chmura", img)
    cv.waitKey()

    img = img.astype(np.float32)/255.
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    Xdata = []
    Ydata = []
    Zdata = []
    colors = []
    max = 0
    for y in range(0,len(img)):
        for x in range(0, len(img[0])):
            tmp = np.linalg.norm(img[y][x])
            if tmp > 0:
                Xdata.append(x)
                Ydata.append(y)
                Zdata.append(tmp)
                colors.append(colors_img[y][x])

    ax.scatter(Xdata[0::50], Ydata[0::50], Zdata[0::50], c = colors[0::50])
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()

if __name__ == '__main__':
    main()