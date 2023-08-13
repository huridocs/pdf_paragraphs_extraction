from pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration

config_json = {
    "num_class": 2,
    "context_size": 1,
    "num_boost_round": 1000,
    "num_leaves": 149,
    "learning_rate": 0.1,
    "lambda_l1": 6.557567e-08,
    "lambda_l2": 2.3948e-07,
    "feature_fraction": 0.4,
    "bagging_fraction": 1.0,
    "bagging_freq": 0,
    "min_data_in_leaf": 20,
    "seed": 22,
}

MODEL_CONFIGURATION = ModelConfiguration(**config_json)

if __name__ == "__main__":
    print(MODEL_CONFIGURATION)
