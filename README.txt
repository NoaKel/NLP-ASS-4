# extract:
python extracy.py path_to_train_txt path_to_dev_txt path_to_train_annotations path_to_dev_annotations

inputs:
path_to_train_txt - path to train corpus, please use *.txt
path_to_dev_txt - path to dev corpus, please use *.txt
path_to_train_annotations - path to train annotations (compulsory) 
path_to_dev_annotations - path to dev annotations (compulsory) 

outputs:
DEV.annotations.Pred - predicted dev annotation file
TRAIN.annotations.Pred - predicted train annotation file

# eval:
python eval.py path_to_gold_annotations path_to_pred_annotations

inputs:
path_to_gold_annotations
path_to_pred_annotations

outputs:
N/A

 
