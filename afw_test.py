# From SimonK's tutorial
# 3/31/2017 -- MSSG

import sys
import lsst.afw.image as afwImage
import lsst.afw.geom as afwGeom
from lsst.pex.exceptions import LengthError
import lsst.afw.math as afwMath
import lsst.afw.detection as afwDetect
import lsst.afw.display as afwDisplay
  
n_objects = 1000

box = afwGeom.BoxI(afwGeom.PointI(300, 500),
                   afwGeom.ExtentI(2000, 2048))

im = afwImage.ImageF(box)

print("im.getXY0() = ", im.getXY0())

subbox = afwGeom.BoxI(afwGeom.PointI(10, 10),
                       afwGeom.ExtentI(100, 100))

try:
     im2 = afwImage.ImageF(im, subbox)
except LengthError:
     im2 = afwImage.ImageF(im, subbox, afwImage.LOCAL)

print("im2.getXY0() = ", im2.getXY0())
     
rand = afwMath.Random()
buffer_xy = 150 # Don't put objects near the edges
x_positions = [rand.uniformInt(im.getWidth() - 2*buffer_xy)
                + buffer_xy for i in xrange(n_objects)]
y_positions = [rand.uniformInt(im.getHeight() - 2*buffer_xy)
                + buffer_xy for i in xrange(n_objects)]


print("x_positions , y_positions = ", x_positions , y_positions )

display = afwDisplay.getDisplay()
display.setMaskTransparency(50, None)
psf_size = 121 # This has to be odd
sigma = 0.7/0.2 # seeing in arcsec/pixel size in arcsec
peak_val = 6000
psf = afwDetect.GaussianPsf(psf_size, psf_size, sigma)
psf_im = psf.computeImage()

print("psf = ", psf)

print("psf_im = ", psf_im)


for x, y in zip(x_positions, y_positions):
     x0 = x - (psf_size - 1)/2
     y0 = y - (psf_size - 1)/2
     box = afwGeom.BoxI(afwGeom.PointI(x0, y0),
                        afwGeom.ExtentI(psf_size, psf_size))
     subim = afwImage.ImageF(im, box, afwImage.LOCAL)


try:
         subim += psf_im
except NotImplementedError:
         psf_im = psf_im.convertF()
         subim += psf_im

print(" subim = ", subim)

back_im = afwImage.ImageF(im.getBBox())
afwMath.randomPoissonImage(back_im, rand, 100)
im += back_im
display.mtv(im)
display.incrDefaultFrame()
mask = afwImage.MaskU(im.getBBox())
masked_im = afwImage.MaskedImageF(im, mask, im)         

sys.exit()




threshold = afwDetect.createThreshold(5., 'stdev')
fs = afwDetect.FootprintSet(masked_im, threshold, 'DETECTED')
#display.mtv(masked_im)
#display.incrDefaultFrame()




bctrl = afwMath.BackgroundControl(11, 11)
bkgd = afwMath.makeBackground(masked_im, bctrl)
masked_im -= bkgd.getImageF()
masked_im.getMask().set(0) # reset mask
fs = afwDetect.FootprintSet(masked_im, threshold,'DETECTED')
#display.mtv(masked_im)
#display.incrDefaultFrame()


# numpy arrays from images
im, mask, var = masked_im.getArrays()
print type(im)
print im.dtype


# arrays are views
xy0 = masked_im.getXY0()
xy0 = masked_im.getXY0()
xy0.shift(afwGeom.ExtentI(100, 120))
box = afwGeom.BoxI(xy0, afwGeom.ExtentI(100, 100))
subim = afwImage.ImageF(masked_im.getImage(), box)
sub_arr = subim.getArray()
sub_arr[:][:] = im.max()
display.mtv(masked_im)




# The >>= operator
left_box = afwGeom.BoxI(afwGeom.PointI(0,0),
                         afwGeom.ExtentI(1000, 2048))
right_box = afwGeom.BoxI(afwGeom.PointI(1000, 0),
                          afwGeom.ExtentI(1000, 2048))
im = masked_im.getImage()
new_im = afwImage.ImageF(masked_im.getBBox())
left_subim = afwImage.ImageF(im, left_box, afwImage.LOCAL)
right_subim = afwImage.ImageF(im, right_box, afwImage.LOCAL)
left_subim *= -1
new_subim = afwImage.ImageF(new_im, left_box, afwImage.LOCAL)
new_subim <<= left_subim
new_subim = afwImage.ImageF(new_im, right_box, afwImage.LOCAL)
new_subim <<= right_subim


display.mtv(new_im)

sys.exit()
