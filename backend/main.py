from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne
import io
import base64
from typing import List
import tempfile
import os
import warnings
import logging
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_csv_data(file_content: bytes, filename: str) -> mne.io.Raw:
    try:
        logger.info(f"Processing file: {filename}")
        
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
            logger.info(f"Created temporary file: {temp_file_path}")

        # Read the CSV file
        try:
            # First read the file to get the header
            with open(temp_file_path, 'r') as f:
                header = f.readline().strip()
            
            # Split the header by tab and then by comma
            columns = header.split('\t')[0].split(',')
            logger.info(f"Columns found: {columns}")
            
            # Read the data with the correct separator and handle missing values
            data = pd.read_csv(temp_file_path, sep='\t', names=columns, na_values=['', 'NA', 'NaN'], keep_default_na=True)
            logger.info(f"Successfully read CSV file. Shape: {data.shape}")
            
            # The data is in the timestamps column as a comma-separated string
            # Split it into separate columns
            data_values = data['timestamps'].str.split(',', expand=True)
            data_values.columns = columns
            
            # Skip the first row as it contains column names again
            data_values = data_values.iloc[1:]
            
            # Convert all columns to numeric
            for col in columns:
                if col != 'timestamps':  # Skip the timestamps column
                    data_values[col] = pd.to_numeric(data_values[col], errors='coerce')
            
            logger.info(f"Data head after processing:\n{data_values.head()}")
            logger.info(f"Data types after processing:\n{data_values.dtypes}")
            
            # Check for any completely empty columns
            empty_cols = data_values.columns[data_values.isna().all()].tolist()
            if empty_cols:
                logger.error(f"Empty columns found: {empty_cols}")
                raise ValueError(f"File {filename} contains empty columns: {', '.join(empty_cols)}")
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise ValueError(f"Error reading CSV file {filename}: {str(e)}")
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        logger.info("Cleaned up temporary file")
        
        # Check if required columns exist
        required_columns = ['Fp1', 'Fz', 'F3', 'F7', 'FT9', 'FC5', 'FC1', 'C3', 'T7', 'TP9', 'CP5', 'CP1', 'Pz', 'P3', 'P7', 'O1', 'Oz', 'O2', 'P4', 'P8', 'TP10', 'CP6', 'CP2', 'C4', 'T8', 'FT10', 'FC6', 'FC2', 'F4', 'F8', 'Fp2']
        missing_columns = [col for col in required_columns if col not in data_values.columns]
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            raise ValueError(f"Missing required columns in {filename}: {', '.join(missing_columns)}")
        
        # Check for non-numeric values
        for col in required_columns:
            non_numeric = data_values[col][data_values[col].isna()]
            if not non_numeric.empty:
                logger.error(f"Non-numeric values found in column {col}: {non_numeric.head()}")
                raise ValueError(f"Column {col} in {filename} contains non-numeric values")
        
        # Extract EEG data
        eeg_data = data_values[required_columns].values.T
        logger.info(f"Extracted EEG data shape: {eeg_data.shape}")
        
        # Check for NaN or infinite values
        if np.any(np.isnan(eeg_data)) or np.any(np.isinf(eeg_data)):
            logger.error("NaN or infinite values found in data")
            raise ValueError(f"Data in {filename} contains NaN or infinite values")
        
        # Create info object
        ch_names = required_columns
        ch_types = ['eeg'] * len(ch_names)
        info = mne.create_info(ch_names=ch_names, ch_types=ch_types, sfreq=250)
        
        # Create Raw object
        raw = mne.io.RawArray(eeg_data, info)
        logger.info("Successfully created MNE Raw object")
        
        # Set up the standard 10-20 montage
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage)
        logger.info("Set up standard 10-20 montage")
        
        # Apply bandpass filter
        raw.filter(l_freq=1, h_freq=40)
        logger.info("Applied bandpass filter")
        
        # Apply notch filter to remove power line interference
        raw.notch_filter(freqs=50)
        logger.info("Applied notch filter")
        
        return raw
    except Exception as e:
        logger.error(f"Error in load_csv_data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

def plot_raw_eeg(raw: mne.io.Raw, title: str) -> str:
    try:
        plt.style.use('default')  # Use default style as base
        plt.figure(figsize=(20, 12))
        
        # Plot with improved styling
        raw.plot(duration=5, n_channels=31, scalings='auto', title=title,
                highpass=1, lowpass=40, show_options=True, block=False)
        
        # Customize the plot
        plt.gca().set_facecolor('#f8f9fa')
        plt.gcf().set_facecolor('white')
        plt.xlabel('Time (s)', fontsize=12)
        plt.ylabel('Amplitude (µV)', fontsize=12)
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save plot to base64 string with higher DPI
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating raw EEG plot: {str(e)}")

def plot_psd(raw: mne.io.Raw, title: str) -> str:
    try:
        plt.style.use('default')  # Use default style as base
        plt.figure(figsize=(15, 8))
        
        # Compute and plot PSD with improved styling
        psd = raw.compute_psd(method='welch', fmin=1, fmax=40)
        psd.plot(picks='all', show=False)
        
        # Customize the plot
        plt.gca().set_facecolor('#f8f9fa')
        plt.gcf().set_facecolor('white')
        plt.title(title, fontsize=16, pad=20, fontweight='bold')
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Set y-axis limits for better visibility
        plt.ylim(-40, 20)
        
        # Customize line appearance
        for line in plt.gca().get_lines():
            line.set_linewidth(2)
            line.set_color('#2ecc71')
        
        plt.tight_layout()
        
        # Save plot to base64 string with higher DPI
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PSD plot: {str(e)}")

def plot_topomap(raw: mne.io.Raw, band: str, title: str) -> str:
    try:
        plt.style.use('default')  # Use default style as base
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Calculate power spectral density using the newer method
        psd = raw.compute_psd(method='welch', fmin=1, fmax=40)
        
        # Define frequency bands
        bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 40)
        }
        
        if band not in bands:
            raise ValueError(f"Invalid frequency band: {band}")
        
        # Get band power
        fmin, fmax = bands[band]
        
        # Get the data for the specific frequency band
        band_idx = np.where((psd.freqs >= fmin) & (psd.freqs <= fmax))[0]
        band_power = np.mean(psd.get_data()[:, band_idx], axis=1)
        
        # Create info object for plotting
        info = raw.info
        
        # Plot topomap with improved styling
        im, _ = mne.viz.plot_topomap(band_power, info, show=False, cmap='viridis',
                                   contours=6, outlines='head', sphere=0.15, axes=ax)
        
        # Customize the plot
        ax.set_facecolor('#f8f9fa')
        fig.set_facecolor('white')
        plt.title(title, fontsize=16, pad=20, fontweight='bold')
        
        # Add colorbar with custom styling
        cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.1)
        cbar.set_label('Power (µV²/Hz)', fontsize=12)
        
        plt.tight_layout()
        
        # Save plot to base64 string with higher DPI
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating topomap: {str(e)}")

def plot_band_powers(raws: List[mne.io.Raw], band: str) -> str:
    try:
        plt.style.use('default')  # Use default style as base
        plt.figure(figsize=(12, 8))
        
        # Define frequency bands
        bands = {
            'delta': (1, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 40)
        }
        
        if band not in bands:
            raise ValueError(f"Invalid frequency band: {band}")
        
        # Get band power for each condition
        fmin, fmax = bands[band]
        band_powers = []
        
        for raw in raws:
            psd = raw.compute_psd(method='welch', fmin=fmin, fmax=fmax)
            power = psd.get_data().mean(axis=1)
            band_powers.append(power)
        
        # Create bar plot with improved styling
        conditions = ['Before Music', 'During Music', 'After Music']
        x = np.arange(len(conditions))
        width = 0.35
        
        # Use a modern color palette
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        
        bars = plt.bar(x, [np.mean(power) for power in band_powers], width,
                      color=colors, alpha=0.8)
        
        # Add error bars
        plt.errorbar(x, [np.mean(power) for power in band_powers],
                    yerr=[np.std(power) for power in band_powers],
                    fmt='none', color='black', capsize=10, capthick=2)
        
        # Customize the plot
        plt.gca().set_facecolor('#f8f9fa')
        plt.gcf().set_facecolor('white')
        plt.title(f'{band.capitalize()} Band Power Comparison', fontsize=16, pad=20, fontweight='bold')
        plt.xlabel('Condition', fontsize=12)
        plt.ylabel(f'{band.capitalize()} Band Power (µV²/Hz)', fontsize=12)
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Customize x-axis
        plt.xticks(x, conditions, fontsize=10)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save plot to base64 string with higher DPI
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating band power plot: {str(e)}")

@app.post("/analyze")
async def analyze_eeg(
    before_music: UploadFile = File(...),
    during_music: UploadFile = File(...),
    after_music: UploadFile = File(...)
):
    try:
        logger.info("Starting EEG analysis")
        logger.info(f"Files received: {before_music.filename}, {during_music.filename}, {after_music.filename}")

        # Validate file types
        if not all(file.filename.endswith('.csv') for file in [before_music, during_music, after_music]):
            logger.error("Invalid file type detected")
            raise HTTPException(
                status_code=400,
                detail="All files must be CSV files. Please ensure all files have the .csv extension."
            )

        # Read file contents
        try:
            before_content = await before_music.read()
            during_content = await during_music.read()
            after_content = await after_music.read()
            logger.info("Successfully read all file contents")
        except Exception as e:
            logger.error(f"Error reading files: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error reading files: {str(e)}"
            )

        # Process the files
        try:
            before_raw = load_csv_data(before_content, before_music.filename)
            during_raw = load_csv_data(during_content, during_music.filename)
            after_raw = load_csv_data(after_content, after_music.filename)
            logger.info("Successfully processed all files")
        except HTTPException as he:
            logger.error(f"Error processing files: {str(he)}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error processing files: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error processing EEG data: {str(e)}"
            )
        
        # Generate plots
        try:
            logger.info("Starting plot generation")
            results = {
                'raw_plots': {
                    'before': plot_raw_eeg(before_raw, 'Raw EEG - Before Music'),
                    'during': plot_raw_eeg(during_raw, 'Raw EEG - During Music'),
                    'after': plot_raw_eeg(after_raw, 'Raw EEG - After Music')
                },
                'psd_plots': {
                    'before': plot_psd(before_raw, 'Power Spectral Density - Before Music'),
                    'during': plot_psd(during_raw, 'Power Spectral Density - During Music'),
                    'after': plot_psd(after_raw, 'Power Spectral Density - After Music')
                },
                'topomaps': {
                    'delta': {
                        'before': plot_topomap(before_raw, 'delta', 'Delta Band Topography - Before Music'),
                        'during': plot_topomap(during_raw, 'delta', 'Delta Band Topography - During Music'),
                        'after': plot_topomap(after_raw, 'delta', 'Delta Band Topography - After Music')
                    },
                    'theta': {
                        'before': plot_topomap(before_raw, 'theta', 'Theta Band Topography - Before Music'),
                        'during': plot_topomap(during_raw, 'theta', 'Theta Band Topography - During Music'),
                        'after': plot_topomap(after_raw, 'theta', 'Theta Band Topography - After Music')
                    },
                    'alpha': {
                        'before': plot_topomap(before_raw, 'alpha', 'Alpha Band Topography - Before Music'),
                        'during': plot_topomap(during_raw, 'alpha', 'Alpha Band Topography - During Music'),
                        'after': plot_topomap(after_raw, 'alpha', 'Alpha Band Topography - After Music')
                    },
                    'beta': {
                        'before': plot_topomap(before_raw, 'beta', 'Beta Band Topography - Before Music'),
                        'during': plot_topomap(during_raw, 'beta', 'Beta Band Topography - During Music'),
                        'after': plot_topomap(after_raw, 'beta', 'Beta Band Topography - After Music')
                    },
                    'gamma': {
                        'before': plot_topomap(before_raw, 'gamma', 'Gamma Band Topography - Before Music'),
                        'during': plot_topomap(during_raw, 'gamma', 'Gamma Band Topography - During Music'),
                        'after': plot_topomap(after_raw, 'gamma', 'Gamma Band Topography - After Music')
                    }
                },
                'band_powers': {
                    'delta': plot_band_powers([before_raw, during_raw, after_raw], 'delta'),
                    'theta': plot_band_powers([before_raw, during_raw, after_raw], 'theta'),
                    'alpha': plot_band_powers([before_raw, during_raw, after_raw], 'alpha'),
                    'beta': plot_band_powers([before_raw, during_raw, after_raw], 'beta'),
                    'gamma': plot_band_powers([before_raw, during_raw, after_raw], 'gamma')
                }
            }
            logger.info("Successfully generated all plots")
        except Exception as e:
            logger.error(f"Error generating plots: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating plots: {str(e)}"
            )
        
        return results
    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 