# GlassyIonicConductorDatabase

- Contains daily experimental data of polymeric ionic conductors
  
  - Process (as flowchart), structure, measurements, and properties

- Data are processed by machine learning tools

# How to start

- Run "Load_graph.ipynb"
  
  - This is a main script of machine learning

- "Parse_****.ipynb" are measurement data processing modules
  
  - Whenever the database is updated, they should be run

# Requirements

- Check for env. yml
  
  - Includes some unnecessary modules (to be fixed)

- Main modules
  
  - netrowkX (e.g., 2.5)
  
  - transformers (e.g., 2.1.1) and BERT model (PyTorch or TensorFlow)
  
  - pandas, scikit-learn, matplotlib, etc.
  
  - boruta_py (e.g., 0.3)
  
  - pyvis (e.g., 0.1.9)

- This database is processed by "FlowMater", which can treat graph data.
  
  - Visit the following URL for the latest version.
  
  - https://github.com/KanHatakeyama/FlowMater2

# Related paper

- TBD

# History

- version 2022.1.**: initial version

# Author

- Kan Hatakeyama-Sato
- Waseda University
- [Kan Hatakeyama](https://kanhatakeyama.github.io/)
- [satokan@toki.waseda](mailto:satokan@toki.waseda).(japan)
