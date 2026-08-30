mkdir -p raw/nis/{2015..2024}

# 2015
wget -nc -P raw/nis/2015 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF15.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF15.SAS

# 2016
wget -nc -P raw/nis/2016 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF16.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NISPUF16.SAS

# 2017
wget -nc -P raw/nis/2017 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF17.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF17.SAS

# 2018
wget -nc -P raw/nis/2018 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF18.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF18.SAS

# 2019
wget -nc -P raw/nis/2019 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF19.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF19.SAS

# 2020
wget -nc -P raw/nis/2020 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF20.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF20.SAS

# 2021
wget -nc -P raw/nis/2021 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF21.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF21.SAS

# 2022
wget -nc -P raw/nis/2022 \
  https://ftp.cdc.gov/pub/Vaccines_NIS/NISPUF22.DAT \
  https://www.cdc.gov/vaccines/imz-managers/nis/downloads/NIS-PUF22.SAS

# 2023
wget -nc -P raw/nis/2023 \
  https://www.cdc.gov/nis/media/files/2024/11/NISPUF23.DAT \
  https://www.cdc.gov/nis/media/files/2024/11/NISPUF23.SAS

# 2024
wget -nc -P raw/nis/2024 \
  https://www.cdc.gov/nis/media/files/2026/05/NISPUF24.DAT \
  https://www.cdc.gov/nis/media/files/2026/05/NISPUF24.SAS