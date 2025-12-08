
# A RTK-based UAV System for Real-Time Pest Detection in Opuntia ficus-indica Crops

This repository contains the code and resources for the project "A RTK-based UAV System for Real-Time Pest Detection in Opuntia ficus-indica Crops", as described in the paper by S. Shimura, A. Miyazaki, M. Frye, and R. Mansano.

## Overview

The cultivation of *Opuntia ficus-indica* (prickly pear cactus) is under critical threat from pests like the *Cactoblastis cactorum* moth. This project presents a novel, two-stage automated system using Unmanned Aerial Vehicles (UAVs) to create precise pest detection maps. The system is designed to enable early and targeted interventions, minimizing crop losses and reducing the environmental impact of pesticides.

This work is an extension of a successful indoor pilot project and aims to apply the system in a real-world field environment.

## How It Works

The system operates in two main stages, comprising four steps:

### Stage 1: High-Precision Mapping and Route Planning

1.  **High-Resolution Mapping:** A drone equipped with Real-Time Kinematics (RTK) flies at a high altitude to capture images of the crop. These images are used to generate a high-precision georeferenced orthomosaic map with a centimeter-level ground sample distance (GSD).

2.  **Image Processing and Route Planning:**
    *   The high-resolution map is processed using the **Segment Anything Model (SAM)** to segment the crop rows.
    *   An AI algorithm identifies the centerlines between the rows to generate optimized flight paths for a low-altitude survey.

### Stage 2: Low-Altitude Survey and Real-Time Detection

3.  **Low-Altitude Survey:** A second drone flies along the optimized, low-altitude paths, streaming video to a base station.

4.  **AI-Based Pest Detection and Map Generation:**
    *   A **YOLOv8n** model running on a Jetson Orin Nano processes the video stream in real-time to detect pests such as the *Cactoblastis cactorum* moth, cochineal scale, and fungi.
    *   The system records the geolocation of each detection and generates a final pest infestation map.

## Technologies Used

*   **Hardware:**
    *   DJI Mavic 3 Enterprise with RTK
    *   Jetson Orin Nano
*   **Software & Models:**
    *   **YOLOv8n:** For real-time pest detection.
    *   **Segment Anything Model (SAM):** For crop row segmentation.
    *   **WebODM:** For generating high-resolution orthomosaics and Digital Surface Models (DSMs).
    *   **Python:** For automation scripts and model execution.
    *   **OBS Studio & MediaMTX:** For video streaming simulation.

## Repository Structure

```
.
├───README.md
├───data/
│   ├───raw_images/       # Raw images from high-altitude flights
│   └───processed_maps/   # Orthomosaics and DSMs
├───notebooks/
│   ├───1_segment.ipynb   # Notebook for crop row segmentation with SAM
│   └───2_route.ipynb     # Notebook for generating flight paths
├───scripts/
│   ├───yolo_fast.py      # Script for real-time pest detection
│   ├───geolocation.py    # Script for cross-referencing timestamps and GPS data
│   └───map_gen.py        # Script for generating the final pest infestation map
└───models/
    └───prickly_pear_health.pt  # Trained YOLOv8n model
```

## Installation

To set up the environment and run the code in this repository, please follow these steps:

```bash
# 1. Clone the repository
git clone https://github.com/sergioshimura/Pest-Detection.git
cd Pest-Detection

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install the required dependencies
pip install -r requirements.txt
```
*(Note: A `requirements.txt` file should be created to list all necessary Python packages.)*

## Usage

1.  **Generate the Orthomosaic:** Use the images in the `data/raw_images` directory with WebODM to create a high-resolution map.
2.  **Segment and Plan Routes:** Run the `notebooks/1_segment.ipynb` and `notebooks/2_route.ipynb` to generate the flight paths.
3.  **Run Pest Detection:** Use the `scripts/yolo_fast.py` script with a video stream to perform real-time detection.
4.  **Generate the Final Map:** Execute `scripts/geolocation.py` and `scripts/map_gen.py` to create the pest infestation map.

## Results

The field experiments were conducted in Vinhedo-SP, Brazil. At an average survey speed of 0.95 m/s, the system achieved:

*   **Precision:** 100%
*   **Recall:** 70%
*   **Accuracy:** 95.2%
*   **F1-Score:** 82.4%

The AI model's inference time was **52.37 ms** on a Jetson Orin Nano, confirming its feasibility for real-time applications.

## Future Work

*   Improve the AI model's accuracy by building a more robust and diverse dataset.
*   Integrate the separate programs and processes into a single, user-friendly application.
*   Explore the use of NTRIP services for large-scale implementations without a local RTK base station.

## Citation

If you use this work, please cite the original paper:

Shimura, S., Miyazaki, A., Frye, M., & Mansano, R. (2024). A RTK-based UAV System for Real-Time Pest Detection in Opuntia ficus-indica Crops. *HOLOS*, 40(1), eXXXX.

## Acknowledgements

The authors would like to thank Mr. Gilson de Lima Raeder, owner of the Prickly Pear farm in Vinhedo, the AVS lab at University of the Incarnate Word and Prof. Ronaldo Mansano from USP for their support.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
