

## Steps to Download, Process and Store the Dataset:

### Mounting EBS volume with EC2

1. **Launch Instance with EBS volume**
    Launch the instance with EBS volume of 400 GB by clicking add volume just below the root volume while configuring the instance. 

2. **Check the name**
    ```
    lsblk
    ```
    ```
    df -h
    ```
3. **Mount the volume**
    ```
    sudo mkdir /mnt/dataEBS
    ```

    ```
    sudo mount /dev/nvme1n1 /mnt/dataEBS
    ```

    For Kaggle to download the dataset directly in the volume, move to directory
    ```
    sudo chmod -R 777 /mnt/dataEBS
    ```



### Downloading from Kaggle

1. **Install Kaggle CLI**:
   Ensure you have the Kaggle CLI installed. You can install it using pip:
   ```bash
   pip install kaggle
   ```

2. **Authenticate**:
   - Go to [Kaggle Account Settings](https://www.kaggle.com/account).
   - Scroll down to the "API" section and click on "Create New API Token."
   - This will download a file named `kaggle.json`. Save it securely.
   - Place the `kaggle.json` file in the directory `~/.kaggle/` (Linux/Mac) or `%USERPROFILE%\.kaggle\` (Windows).
   - Ensure the file has proper permissions:
     ```bash
     chmod 600 ~/.kaggle/kaggle.json
     ```

3. **Download the Dataset**:
   Run the following command:
   ```bash
   kaggle competitions download -c imagenet-object-localization-challenge
   ```

4. **Extract the Dataset**:
   Once the dataset is downloaded, extract it using:
   ```bash
   unzip -q imagenet-object-localization-challenge.zip -d /path/to/extract/
   ```

### Convert the val dataset to proper format as train

1. **Run the script**:
    ```
    python convert_val.py -d /mnt/dataEBS/imagenet/ILSVRC/Data/CLS-LOC/val -l /mnt/dataEBS/imagenet/LOC_val_solution.csv
    ```


### Notes:
- You may need sufficient disk space (~320 GB after unzipping).

