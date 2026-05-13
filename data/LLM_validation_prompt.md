Method,N_total,Coverage,N_eval,TP,FP,TN,FN,Accuracy,Precision,Recall,F1,Note
Dictionary rule,600,1.0,600,216,84,300,0,0.86,0.72,1.0,0.8372093023255813,Positive if the passage is a dictionary hit.
GPT-5.5 / Claude strict consensus,600,0.45166666666666666,271,121,0,82,68,0.7490774907749077,1.0,0.6402116402116402,0.7806451612903226,Evaluated only where GPT-5.5 and Claude agree; non-hit and disagreement rows are abstentions.
FinBERT fine-tuned on strict consensus,600,1.0,600,151,83,301,65,0.7533333333333333,0.6452991452991453,0.6990740740740741,0.6711111111111111,Backbone: yiyanghkust/finbert-tone-chinese; train rows exclude dictionary-hit gold passages.
Hybrid consensus with dictionary fallback,600,1.0,600,148,2,382,68,0.8833333333333333,0.9866666666666667,0.6851851851851852,0.8087431693989071,"Uses strict LLM consensus on covered hit rows; falls back to dictionary rule for non-hit, missing, or disagreement rows."
