# MSF.1004.321

Source: `planning/sources/raw/MSF.1004.321.pdf`

Materials Science Forum
ISSN: 1662-9752, Vol. 1004, pp 321-327
doi:10.4028/www.scientific.net/MSF.1004.321
© 2020 Trans Tech Publications Ltd, All Rights Reserved

Submitted: 2019-09-19
Revised: 2019-11-19
Accepted: 2020-02-07
Online: 2020-07-28

From Wafers to Bits and Back again:
Using Deep Learning to Accelerate the Development and
Characterization of SiC
R. Leonard1*, M. Conrad1, E. Van Brunt1, J. Giles1, E. Hutchins1, E. Balkas1
1Wolfspeed, A Cree Company, 4600 Silicon Dr. Durham, NC 27703 USA

*Robert.Leonard@wolfspeed.com

Keywords:  Non-destructive  testing,  Deep  Learning,  DCNN,  Machine  Learning,  Defect  Etching,
Photoluminescence,  Dislocations,  basal  plane  dislocations,  BPD,  threading  screw  dislocations,
TSD, threading edge dislocations, TED, SXRT

Abstract.  A non-destructive, fast and accurate extended defect counting method on large diameter
SiC  wafers  is  presented.    Photoluminescence  (PL)  signals  from  extended  defects  on  4H-SiC
substrates were correlated to the specific etch features of Basal Plane Dislocations (BPDs), Threading
Screw  Dislocations  (TSDs),  and  Threading  Edge  Dislocations  (TED).    For  our  non-destructive
technique (NDT), automated defect detection was developed using modern deep convolutional neural
networks (DCNN).  To train a robust network, we used our large volume data set from our selective
etch method of 4H-SiC substrates, already established based on definitive correlations to Synchrotron
X-Ray Topography (SXRT) [1].  The defect locations, classifications and counts determined by our
DCNN  correlate  with  the  subsequently  etch-delineated  features  and  counts.    Once  our  network  is
sufficiently trained we will no longer need destructive methods to characterize extended defects in
4H-SiC substrates.

Introduction

The  use  of  silicon  carbide  accelerates  the  automotive  industry’s  transformation  to  electric
vehicles, enabling greater system efficiencies, while reducing cost, lowering weight and conserving
space  [2].    Wolfspeed,  as  the  largest  volume  SiC  substrate  producer,  fuels  this  transformation  by
improving the quality and increasing the size of commercial SiC wafers [3].  Increased device yields
and  manufacturing  efficiency  require  continual  reduction  in  extended  defects  [4,  5].    The  quick,
accurate and standardized characterization of these defects is essential for crystal growth technology
development and to provide reliable information to customers.

The goal of this work is to provide a non-destructive defect count method for SiC that can be
implemented  in  the  high-volume  manufacturing  environment.    With  the  non-destructive  method,
wafers can be characterized and subsequently used for device fabrication, vastly reducing the expense
of the characterization process.  This advancement mainly accelerates the feedback loop for tighter
process control in high volume production.  Congruently, it opens additional development pathways
for higher yielding device processing.

Traditionally,  counting  extended  defects  in SiC  is  done  by  delineating  etch  pits  and  counting
them manually, or more recently, with automated microscopy tools.  Etching reveals features that can
be  consistently  recognized  and  correlated  to  other  accepted  characterization  methods  such  as,
synchrotron x-ray topography SXRT [1].  Wafer etching, however, is destructive, expensive, requires
corrosive chemistries and constant attention to maintain a viable process.  Furthermore, only a few
wafers  per  crystal  can  be  sampled,  limiting  the  amount  of  information  available  for  process
improvement and control.

Photoluminescence as a non-destructive technique (PL-NDT) can be used to produce images of
unetched wafers.  Mapping the ultraviolet (UV) excited photoluminescence (PL) emission in a SiC
wafer  is  useful  to  understand  the  distribution  of  the  defects  in  the  substrate  underlying  potential
devices to be fabricated.  PL has been established as a characterization method for extended defects in

All rights reserved. No part of contents of this paper may be reproduced, processed or transmitted in any form or by any means without the written
permission of Trans Tech Publications Ltd, www.scientific.net. (#805152554, Technical University of Munich, Muenchen, Germany-06/06/26,12:27:19)

322

Silicon Carbide and Related Materials 2019

epitaxial 4H-SiC [6], and extended to bulk characterization and wafer mapping by others [7-9].  As
pointed out in the literature, the illuminated defects are near surface only, due to the small penetration
depth of the UV excitation.  Our effort combines etch defect information to classify the defect type
and pinpoint the location in a signal obtained from PL-NDT imaging.

Recently, deep convolutional neural networks (DCNN) have dominated computer vision tasks
such as image classification and object detection in a host of different contexts from cell phones to
satellite images and MRI’s [10-16].  Its success can be attributed to its ability to build and learn a
complex combination of image filters for the specific task at hand.  For a DCNN to learn to correctly
classify an image or locate an object within an image, many annotated images are needed to achieve a
result that generalizes features well.  During the training process, DCNN receives an input image and
processes it through the network of convolutional layers.  The output of the DCNN is a probability
distribution  of  classes  and  pixel  locations.    The  objective  of  the  DCNN  is  to  minimize  the  error
between the predicted class/location and annotated class/location.

Materials and Equipment

In  this  work,  150mm  4°  off  axis  {0001}  double  side  CMP  n-type  4H-SiC  wafers  were
characterized  with  a  LaserTec  Sica88  automatic  scanning  optical  microscopy  equipped  with  PL
capability.  PL and surface images were acquired for: 1.  both Si and C face CMP wafers, and 2. post
defect etching to delineate the etch pit defects for BPD, TD, and TSD’s, as reported in [1].  A near
infrared (NIR) long pass filter was placed before the detector to discriminate the NIR PL emission.
The resulting images were processed as necessary to align features on both faces of the same wafer
for characterization.

Results and Discussion

Typical images for both Si and C faces for the as polished and etched wafer are shown in Fig. 1
and Fig. 2.  Fig. 1(a) shows the PL image of a portion of the measured 4H-SiC 4° off axis Si face
(0001) wafer, with dark linear and concentrated dark spots in a (somewhat) noisy background.  This is
consistent with the work of Kawahara [9], where PL imaging produced light and dark contrast regions
corresponding to dislocations in the near surface (~ <10μm) bulk n-type wafer.  The corresponding
positions  in  the  image  in  Fig.  1 (b) reveal  the  etch  pit  associated  with  the  PL  features.    On  close
examination of these images, the linear features of the PL image correspond to scalloped shaped BPD
etch pits and the dark spots correspond to rounded or even somewhat hexagonal etch pits, in some
cases, which correspond to threading dislocations (TD), either threading edge (TED), or threading
screw (TSD).  From SXRT observations coupled with 4H-SiC defect etching, Sumakeris [1] reported
on the inability to determine if the etch pit was of edge or screw nature just from etching the Si face;
the C face etch was needed to determine which etch feature were TSD.  Fig. 2, similarly, shows the
PL  image  (a)  and  corresponding  etch  image  for  the  C  face.    PL  dark  spots  are  marked  with  their
respective etch feature.  Not surprisingly, due to the difference in etching nature of the Si and C faces,
not  all  C  face  dislocation  etch  pits  correspond  to the  PL  signal  dark  spots,  and  none  of  the  linear
features have a corresponding scalloped BPD etch pit.

Materials Science Forum Vol. 1004

323

200 μm

200 μm

(a)

(b)

Fig.  1.   Example  of  a Si  face  PL-NDT  signal  (a)  with  example  corresponding  etch  pit  image (b).
Linear features within ovals in (a) correspond to scalloped shaped BPD features in (b); dark spots in
(a) correspond to rounded TD features in (b).  Arrows indicate corresponding defect pairs between
images.

200 μm

200 μm

(a)

(b)

Fig. 2.  Example of a C face PL-NDT signal (a) with example corresponding etch pit image (b).  The
PL dark spots correspond to TSD etch pits seen in (b).  Arrows indicate corresponding defect pairs
between images.

The  examples  in  Fig.1  and  Fig.  2  suggest  that,  in  general,  if  you  can  see  the  defect  signal,
PL-NDT or etched, you should be able to count it.  In the case of the etched feature, the contrast is
straight  forward  to  distinguish  features.    The  etch  features  can  be  counted  with  commercially
developed  algorithms.    In  the  PL-NDT  images,  however,  subtle  differences  in  contrast  exist
throughout the image.  To count features from this nuanced signal, we need to use deep convolutional
neural network (DCNN) machine learning for automated defect detection and classification.

324

Silicon Carbide and Related Materials 2019

Inference Pipeline

Training Pipeline

Fig. 3. a) PL-NDT optical micrograph image from Si face wafer as input image; b) micrograph of the
same  wafer  area  imaged  after  etching;  c)  defect  labels  generated  with  automated  microscope
inspection to create the labelled dataset for DCNN training (TD: white, BPD: black); d) etch labels
transferred to PL-NDT image; e) dislocation type and location predicted by DCNN using only the PL
image (TD: white stars, BPD: black dots).  After training the DCNN, the black arrow indicates that
only the PL-NDT measurement image is needed to produce the location and classification required
for defect counting.

Fig. 3 illustrates the production of a DCNN process for non-destructive characterization of SiC.
In Fig. 3 (a) a PL image of the unetched Si face wafer is shown containing features to be associated
with etch defects.  The same wafer is then etched in a eutectic etch bath of NaOH and KOH mixture to
highlight  the  threading  dislocation  (TD)  and  basal  plane  dislocations  (BPD).    The  resultant  etch
features (Fig 3(b)) on the wafer are imaged and labelled (Fig 3(c)) by the scanning optical microscope
and software.  The classified defect positions are converted to a labelling image which are spatially
aligned with the initial PL image.  Fig. 3 (d) shows the defect label image overlay on the PL image.  A
DCNN is trained with thousands of these input image/ label pairs.  Automated optical microscopy
equipped with PL imaging satisfies the need for large DCNN datasets.  Thousands of NDT images are
recorded for each wafer containing many thousands of labelled defects.  The architecture used for the
DCNN is consistent with the state of the art as in references [10-16], with proprietary changes made
to  optimize  performance  on  our  data  set.    Once  the  DCNN  is  trained,  and  using  PL  images  from
unetched wafers taken under conditions similar with those used for the training, the DCNN may be
applied  to  infer  the  type  and  position  of  the  defects,  Fig.  3  (e).    In  this  example,  we  show  the
conditions to detect features for the Si face of a 4H-SiC wafer.  The same process is used to produce a
DCNN for the TSD’s on the C face, using similar images as in Fig. 2, above.  The new C face DCNN
was successful in classifying and locating TSD’s.
  With observations that the PL-NDT images of both C and Si faces are very similar, the DCNN
produced for TSD’s from the C face was applied to the Si Face PL-NDT images, Fig. 4.  The circled
dark features in Fig. 4(a) are the TSD’s found in the near surface Si face PL scan determined by the
DCNN.  As mentioned previously, the TSD etch features on the Si face are not easily determined,
since there are multiple etch behaviours associated with the TSD on the Si face.  Fig. 4(b) shows the
observed etch features of the Si face corresponding to the PL signal, with many threading dislocations

Materials Science Forum Vol. 1004

325

in  the  etch  image,  obscuring  the  actual  position  of  the  TSD’s.    Fig.  4(c),  however,  shows  the
corresponding TSD etch pit (with the x-axis reversed) aligned to the Si face revealing the same pit
pattern as detected by the dark spots in the Si face PL, thus, validating the inferred result.  The ability
to use the C face DCNN on the Si face allows reducing the process to imaging a wafer only once on
the Si face.  This also allows defects to be determined on the face that is closest to the epi surface
being used for devices, regardless of C or Si face.  Furthermore, a limitation on the Si face etch is that
both TED’s and TSD’s are counted at the same time.  With the ability to count the TSD’s on the Si
face, the number of TED’s may be determined as well.

(a)

(b)

400 μm

(c)

Fig. 4. (a) Si face 4H-SiC imaged with PL-NDT.  The circles indicate the DCNN inferred position of
TSD’s from the PL image, not from etch labelling; (b) Defect etched Si face image showing TD and
BPD etch features; (c) Defect etched C face image of same wafer area (reversed on x-axis) revealing
distinct TSD etched features.  All images are from same area on wafer.

Fig. 5 shows initial results as a simple validation of the PL-NDT process to match BPD densities
obtained by the conventional etch process.  For this data set, N=308 wafers were imaged with PL and
subsequently processed through the DCNN network.  A linear fit was applied to NDT values versus
the accepted etch values with a slope of 1.13 and coefficient of determination of the near R2 = 0.84.
Of course, subsequent training and optimizations of the PL-NDT process will occur to improve the
correlation.

Fig. 5.  BPD densities determined by PL-NDT vs. Etch process, with linear fit of data.  (slope=1.13,
R2 = 0.84, N=308).

326

Silicon Carbide and Related Materials 2019

Summary

  We have shown a non-destructive count method for defects in 4H-SiC is not only possible, but is
close  to  being  used  for  defect  reporting  purposes.    Using  non-destructive  PL  images  of  unetched
wafers coupled with automatically labelled images of the corresponding etched wafers as the training
set, DCNN are used to derive a network to infer the position of the defects only from the PL-NDT
scan, regardless of the face scanned.  The defect locations and classifications determined by DCNN
correlate well with the subsequently etch delineated features, used to validate the technique.  After the
DCNN  is  sufficiently  trained  and  validated,  there  is  no  need  to  destroy  wafers  for  defect
characterization,  and  counting  by  etching  will  be phased  out.   Next  steps  involve  comparing  high
volume manufacturing etch defect densities to the DCNN produced densities.

References

[1]   J.J. Sumakeris, R.T. Leonard, E. Deyneka, Y. Khlebnikov, A.R. Powell, J. Seaman, M.J. Paisley,
V. Tsvetkov,  J.  Guo,  Y.  Yang,  M.  Dudley, E.  Balkas,  Dislocation  characterization  in  4H-SiC
crystals, Materials Science Forum, Vol. 858, (2016) pp. 393-396.

[2]   Cree,  Inc.  Press  Release,  Cree  selected  as  silicon  carbide  partner  for  the  Volkswagen  group
https://www.cree.com/news-events/news/article/cree-selected-as-silicon-

FAST
carbide-partner-for-the-volkswagen-group-fast-program, May 14, 2019.

program,

[3]  Cree,  Inc.  Press  Release,  Cree  to  invest  $1  billion  to  expand  silicon  carbide  capacity,
https://www.cree.com/news-events/news/article/cree-to-invest-1-billion-to-expand-silicon-carbi
de-capacity, May 7, 2019.

[4]   R.T. Leonard, M.J. Paisley, S. Bubel, J.J. Sumakeris, A.R. Powell, Y. Khlebnikov, J.C. Seaman,
J. Ambati, A.A. Burk, M.J. O’Loughlin, E. Balkas, Exploration of bulk and epitaxy defects in
4H-siC  using  large  scale  optical  characterization,  Mater.  Sci.  Forum  Vol.  897  (2017)  pp.
226-229.

[5]   E. Van Brunt, A. Burk, D.J. Lichtenwalner, R. Leonard, S.Sabri, D.A. Gajewski, A. Mackenzie,
B.A.  Hull,  S.  Allen,  J.W.Palmour,  Performance  and  reliability  impacts  of  extended  epitaxial
defects on 4H-SiC power devices, Mater. Sci. Forum Vol. 924 (2018) pp.137-142.

[6]   R.E.  Stahlbush,  K.X.  Liu,  Q.Zhang,  J.J.  Sumakeris,  Whole-wafer  mapping  of  dislocations  in

4H-SiC epitaxy, Mater. Sci. Forum Vols. 556-557 (2007), pp. 295-298.

[7]   M. Tajima, E. Higashi, T. Hayashi, H. Kinoshita, H. Shiomi, Characterization of SiC wafers by

photoluminescence mapping, Mater. Sci. Forum Vols. 527-529 (2006) pp.711-716.

[8]   P.Berwian,;  D.  Kaminzky,  K.  Roßhirt;  B.  Kallinger;  J.  Friedrich;  S.  Oppel,  A. Schneider,  M.
Schütz, Imaging defect luminescence of 4H-SiC by ultraviolet-photoluminescence, Solid State
Phenomena, Vol. 242, (2016) pp. 484-489.

[9]   C. Kawahara, J. Suda, T. Kimoto, Identification of dislocations in 4H-SiC epitaxial layers and

substrates using photoluminescence imaging, Jpn. J. Appl. Phys. 53 (2014) 020304.

[10] L.C. Chen, G. Papandreou, Ia. Kokkinos, K. Murphy, A.L. Yuille, DeepLab: Semantic image
segmentation  with  deep  convolutional  nets,  atrous  convolution,  and  fully  connected  CRFs,
https://arxiv.org/abs/1606.00915.

[11]  O.  Ronneberger,  P.  Fischer,  T.  Brox,  U-Net:  Convolutional  networks  for  biomedical  image

segmentation, https://arxiv.org/abs/1505.04597.

[12] P. Isola, J.Y. Zhu, T. Zhou, A.A. Efros, Image-to-image translation with conditional adversarial

networks, https://arxiv.org/abs/1611.07004.

Materials Science Forum Vol. 1004

327

[13] S. Jégou, M. Drozdzal, D.Vazquez, A. Romero, Y. Bengio, The one hundred layers tiramisu:
Fully convolutional DenseNets for semantic segmentation, https://arxiv.org/abs/1611.09326.

[14] C. Szegedy, W. Liu, Y. Jia, P. Sermanet, S. Reed, D. Anguelov, D. Erhan, V. Vanhoucke, A.

Rabinovich, Going deeper with convolutions, https://arxiv.org/abs/1409.4842.

[15] M.A. Kadhim, M.H. Abed, Convolutional Neural Network for Satellite Image Classification. in:
M.  Huk,  M.  Maleszka,  E.  Szczerbicki  (Eds),  Intelligent  Information  and  Database  Systems:
Recent Developments. ACIIDS 2019. Studies in Computational Intelligence, vol 830. Springer,
Cham (2020), pp.165-178.

[16] F. Hoseini, A. Shahbahrami, P. Bayat, An efficient implementation of deep convolutional neural

networks for MRI segmentation, J. Digit. Imaging. Oct;31(5) (2018) pp.738-747.


