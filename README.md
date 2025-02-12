

# **HRA-AMAP 3D Kidney Registration & Error Analysis**
### **Automated Mapping of Anatomical Parts (AMAP) Assessment**: *A 3D organ registration pipeline for aligning and analyzing male kidney models using the HRA-AMAP framework.*

---

### **Project Overview**
This project demonstrates **3D registration, bidirectional projection, and error visualization** of **male left and right kidneys** using the **HRA-AMAP** framework. The pipeline aligns **generic kidney models** with **human anatomical reference models**, allowing for accurate mapping, visualization, and evaluation of registration accuracy.

---

## **📂 Repository Structure**
```
📁 hra-amap-kidney-assessment/
│── 📂 data/                     # Source & Reference Kidney Models
│── 📂 notebooks/                # Jupyter Notebooks for Registration & Error Analysis
│── 📂 figures/                  # Generated Heatmaps, Histograms & Results
│── 📂 results/                  # Exported Registered Models
│── 📜 README.md                 # Documentation (You are Here)
```

---

## **Key Components**
### **1. Forward Projection** *(Generic Kidney → Anatomical Kidney)*
- Loads **generic kidney models** as **source**.
- Loads **human anatomical kidney models** as **target**.
- Runs **rigid & non-rigid registration** using AMAP.
- Saves the **aligned (registered) models**.

### **2. Backward Projection** *(Anatomical Kidney → Generic Kidney)*
- Reverses the transformation.
- Aligns **anatomical kidneys** back to the **generic kidney model**.
- Ensures **bidirectional consistency** in mapping.

### **3. Error Visualization (Heatmap & Histogram)**
- **Computes Signed Distance Field (SDF)** to measure registration accuracy.
- **Visualizes deviations using a heatmap** (colored model).
- **Plots histogram of errors** to analyze distribution.
- **Applies advanced colormap tuning** for better contrast.

---

## **Installation & Setup**

Go through the repo:
```sh
https://github.com/cns-iu/hra-amap.git
```

## **How to Run the Code**
### **1️⃣ Forward & Backward Projection**
Run the following notebooks inside `notebooks/`:
- [`Usage.ipynb`](notebooks/Usage.ipynb) → Registers the kidneys in **one direction**.
- [`Bidirectional_Projections.ipynb`](notebooks/Bidirectional%20Projections.ipynb) → Registers **forward & backward**.

### **2️⃣ Error Visualization**
- [`Registration_Error_Visualization.ipynb`](notebooks/Registration%20ErrorVisualization.ipynb) → Generates **heatmaps & histograms** for error analysis.

### **3️⃣ View Results**
The **aligned kidneys, heatmaps, and histograms** will be saved in:
```
📂 figures/   → Heatmap models & histograms
📂 /data/Kidney/Results/   → Registered kidney models
```

---
## **Issues Faced**  

### **1. Registration Took Too Long to Converge**
- The **AMAP pipeline** was slow, especially for **high-resolution meshes**.
- Large **3D kidney models (millions of vertices)** caused **long computation times**.

### **2. Sometimes Registration Failed Due to Insufficient Correspondences**
- Open3D **warned about "Too few correspondences"**.
- This happened because **initial meshes were too different** in **scale or detail**.

### **3. Large Mesh Files Caused High RAM Usage**
- Full-resolution **GLB models (millions of points)** required **a lot of memory**.
- Crashes occurred when processing **multiple things at once**.

### **4. Computing signed_distance on all vertices (~millions of points) was too slow and caused kernel crashes.**
- Color mapping compressed values too much, making high-error areas look the same as low-error areas.
---

## **Optimization Suggestions**  

### **1. Leverage CUDA & PyTorch for Faster Computation**
- The registration and distance calculations are currently CPU-based.
- Processing large meshes (millions of points) takes hours to complete.

### **2. Use Bayesian Optimization for Auto-Tuning**
- Users must manually adjust lambda, gamma, max_iterations, etc.
- Poor choices lead to bad registration results.

### **3. Use Deep Learning for Better Feature Extraction**
- Feature-based correspondence is limited to basic geometric methods.
- When models have different resolutions or structures, correspondences can be incorrect.

---

## **📬 Submission Details**
**GitHub Repository:** [📌 Link to Repository](https://github.com/mitanshubhoot/hra-amap-kidney-assessment)  
**Submission Date:** February 2025  
**Contact:** mbhoot@iu.edu 

---

## **References**
- **HRA-AMAP GitHub:** [https://github.com/cns-iu/hra-amap](https://github.com/cns-iu/hra-amap)
- **Human Reference Atlas:** [https://humanatlas.io](https://humanatlas.io)
- **Trimesh Documentation:** [https://trimsh.org](https://trimsh.org)
