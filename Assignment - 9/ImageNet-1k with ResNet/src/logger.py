import logging
import os
from datetime import datetime

class TrainingLogger:
    def __init__(self, model_name, log_dir="logs"):
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a unique log file name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{model_name}_{timestamp}.log')
        
        # Configure logger
        self.logger = logging.getLogger(model_name)
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_training_step(self, epoch, batch_idx, loss, accuracy, lr, total_batches):
        """Log training step metrics"""
        self.logger.info(
            f"Training - Epoch: {epoch}, Batch: [{batch_idx}/{total_batches}], "
            f"Loss: {loss:.4f}, Accuracy: {accuracy:.2f}%, LR: {lr:.6f}"
        )
    
    def log_epoch_stats(self, epoch, train_loss, train_acc, epoch_time):
        """Log end of epoch statistics"""
        self.logger.info(
            f"Epoch {epoch} Summary - "
            f"Training Loss: {train_loss:.4f}, "
            f"Training Accuracy: {train_acc:.2f}%, "
            f"Time: {epoch_time:.2f}s"
        )
    
    def log_validation_stats(self, epoch, val_loss, val_acc, val_acc5=None):
        """Log validation statistics"""
        log_msg = (
            f"Validation - Epoch: {epoch}, "
            f"Loss: {val_loss:.4f}, "
            f"Accuracy: {val_acc:.2f}%"
        )
        if val_acc5 is not None:
            log_msg += f", Top-5 Accuracy: {val_acc5:.2f}%"
        self.logger.info(log_msg)
    
    def log_checkpoint(self, epoch, checkpoint_path):
        """Log checkpoint saving"""
        self.logger.info(f"Checkpoint saved - Epoch: {epoch}, Path: {checkpoint_path}")
    
    def log_error(self, error_msg):
        """Log errors"""
        self.logger.error(f"Error occurred: {error_msg}") 