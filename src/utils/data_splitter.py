def split_data_random():
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        phrases,
        classes,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=classes,
    )