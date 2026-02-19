import pickle
import os

MODEL_FOLDER = 'model/artifacts'

try:
    with open(f'{MODEL_FOLDER}/svm_pipeline.pkl', 'rb') as f:
        pipeline = pickle.load(f)
        
    print("Pipeline steps:", pipeline.named_steps.keys())
    classifier = pipeline.named_steps['clf']
    print("Classifier type:", type(classifier))
    print("Has 'coef_':", hasattr(classifier, 'coef_'))
    print("Has 'calibrated_classifiers_':", hasattr(classifier, 'calibrated_classifiers_'))
    
    if hasattr(classifier, 'calibrated_classifiers_'):
        cc = classifier.calibrated_classifiers_[0]
        print("Calibrated classifier type:", type(cc))
        print("CC dir:", dir(cc))
        if hasattr(cc, 'base_estimator'):
             print("Base estimator:", cc.base_estimator)
             print("Base estimator coef_:", hasattr(cc.base_estimator, 'coef_'))
        elif hasattr(cc, 'estimator'):
             print("Estimator:", cc.estimator)
             print("Estimator coef_:", hasattr(cc.estimator, 'coef_'))
             
except Exception as e:
    print(f"Error: {e}")
