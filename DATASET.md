# About the training data

The YOLOv8n weights in `models/prickly_pear_health.pt` were trained on a set of
images of *Opuntia ficus-indica* showing damage by *Cactoblastis cactorum*,
cochineal scale (*Dactylopius* sp.) and fungal lesions, assembled from publicly
reachable web sources for research purposes.

**Those images are not redistributed in this repository.** Their licences were
never cleared for redistribution, and several carry the credit of commercial
picture agencies or of individual photographers. Publishing them here under this
repository's licence would grant rights that the author does not hold.

What is provided instead:

- the **trained weights**, which are the reusable artefact of that training;
- the **code** that produced every stage of the pipeline;
- the **field photographs** in `assets/field_targets/`, taken by the author,
  which document how the printed targets were placed on the cladodes during the
  validation campaign.

Researchers who need the training set to reproduce the training run should
contact the author, who keeps a provenance record of every file.

## Field targets

The ten printed targets used in the field validation are reproductions of
symptom photographs from the sources described above, printed on paper and
affixed to cladodes at surveyed positions. They served as calibration targets
with known ground-truth coordinates, not as a claim of natural infestation. The
rationale is set out in the manuscript describing the campaign.
