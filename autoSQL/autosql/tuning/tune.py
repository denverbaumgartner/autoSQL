import re
import numpy as np

class SQLTuner: 
    """A class to help with the fine tuning of SQL models."""

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def parse_training_info(text):
        lines = text.split("\n")
        parsed_data = {}
        current_epoch = None

        for line in lines:
            # Extract epoch start
            epoch_match = re.search(r'Training Epoch(\d+):', line)
            if epoch_match:
                current_epoch = int(epoch_match.group(1))
                if current_epoch not in parsed_data:
                    parsed_data[current_epoch] = {"steps": {}}
                continue

            # Extract loss after each step, associate with current epoch
            step_loss_match = re.search(r'step (\d+) is completed and loss is (\d+\.\d+)', line)
            if step_loss_match and current_epoch is not None:
                step = int(step_loss_match.group(1))
                loss = float(step_loss_match.group(2))
                parsed_data[current_epoch]["steps"][step] = loss
                continue

            # Extract evaluation info and associate with current epoch
            eval_ppl_match = re.search(r'eval_ppl=tensor\((\d+\.\d+), device=\'cuda:0\'\)', line)
            eval_epoch_loss_match = re.search(r'eval_epoch_loss=tensor\((\d+\.\d+), device=\'cuda:0\'\)', line)
            if eval_ppl_match and eval_epoch_loss_match and current_epoch is not None:
                parsed_data[current_epoch]["eval_ppl"] = float(eval_ppl_match.group(1))
                parsed_data[current_epoch]["eval_epoch_loss"] = float(eval_epoch_loss_match.group(1))

        return parsed_data

    @staticmethod
    def moving_average(data, window_size):
        """Calculate the moving average of a list."""
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid')
