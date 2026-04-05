from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def choose_strategy(
    task_type: str,
    needs_external_knowledge: bool,
    latency_critical: bool,
    data_quality: str,
    domain_specific: bool,
) -> str:
    """Choose a lightweight strategy instead of RAG.
    Args:
        task_type (str): Task category name.
        needs_external_knowledge (bool): Whether external retrieval is needed.
        latency_critical (bool): Whether low latency is critical.
        data_quality (str): Quality level of available data.
        domain_specific (bool): Whether the task is highly specialized.
    """
    normalized_quality = data_quality.strip().lower()
    normalized_task = task_type.strip().lower()

    if domain_specific:
        return 'Use a domain-specific model'

    if normalized_task in {'classification', 'keyword_extraction'}:
        return 'Use classical ML or deterministic rules'

    if latency_critical:
        return 'Use templates or a lightweight local model'

    if normalized_quality in {'low', 'poor'}:
        return 'Use curated rules or validated templates'

    if not needs_external_knowledge:
        return 'Use a direct model without retrieval'

    return 'RAG can be justified for this case'


def build_pipeline() -> Pipeline:
    """Build a simple text classification pipeline.
    Args:
        None (type): No arguments.
    """
    pipeline = Pipeline(
        steps=[
            ('vectorizer', CountVectorizer()),
            ('classifier', LogisticRegression()),
        ]
    )
    return pipeline


def train_model(
    texts: list[str],
    labels: list[int],
) -> Pipeline:
    """Train a lightweight classifier.
    Args:
        texts (list[str]): Training text samples.
        labels (list[int]): Integer labels for training.
    """
    pipeline = build_pipeline()
    pipeline.fit(texts, labels)
    return pipeline


def predict_label(
    model: Pipeline,
    texts: list[str],
) -> list[int]:
    """Predict labels for new texts.
    Args:
        model (Pipeline): Trained classification pipeline.
        texts (list[str]): New input texts.
    """
    predictions = model.predict(texts)
    return predictions.tolist()


if __name__ == '__main__':
    train_texts = [
        'This review is positive and helpful',
        'This product is excellent',
        'This review is negative and disappointing',
        'The service was terrible',
    ]
    train_labels = [1, 1, 0, 0]

    trained_model = train_model(
        texts=train_texts,
        labels=train_labels,
    )

    input_texts = ['The product is great']
    predicted_labels = predict_label(
        model=trained_model,
        texts=input_texts,
    )

    selected_strategy = choose_strategy(
        task_type='classification',
        needs_external_knowledge=False,
        latency_critical=True,
        data_quality='high',
        domain_specific=False,
    )

    print('Strategy:', selected_strategy)
    print('Predictions:', predicted_labels)
