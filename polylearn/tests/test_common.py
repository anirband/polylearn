from nose.tools import assert_raises, assert_raises_regex, assert_greater
from nose.tools import assert_equal
import numpy as np
# import sklearn.utils.estimator_checks
from polylearn import (PolynomialNetworkClassifier, PolynomialNetworkRegressor,
                       FactorizationMachineClassifier,
                       FactorizationMachineRegressor)

# TODO: can't actually pass the test.
# Regressor needs tweaking (augment=True, beta=20) to pass score>0.5
# Classifier is not multi-output.

# def test_check_estimator():
#     sklearn.utils.estimator_checks.check_estimator(PolyClassifier)
#     sklearn.utils.estimator_checks.check_estimator(PolyRegressor)


X = np.array([[-10, -10], [-10, 10], [10, -10], [10, 10]])
y = np.array(['true', 'false', 'false', 'true'])


def check_classify_xor(Clf):
    """Tests that the factorization machine can solve XOR"""
    clf = Clf(tol=1e-2, fit_lower=None, fit_linear=None, random_state=0)
    assert_equal(clf.fit(X, y).score(X, y), 1.0)


def test_classify_xor():
    yield check_classify_xor, PolynomialNetworkClassifier
    yield check_classify_xor, FactorizationMachineClassifier


def check_predict_proba(Clf):
    clf = Clf(loss='logistic', tol=1e-2, random_state=0).fit(X, y)
    y_proba = clf.predict_proba(X)
    assert_greater(y_proba[0], y_proba[1])
    assert_greater(y_proba[3], y_proba[2])


def test_predict_proba():
    yield check_predict_proba, FactorizationMachineClassifier
    yield check_predict_proba, PolynomialNetworkClassifier


def check_predict_proba_raises(Clf):
    """Test that predict_proba doesn't work with hinge loss"""
    pp = Clf(loss='squared_hinge', random_state=0).predict_proba
    assert_raises(ValueError, pp, X)


def test_predict_proba_raises():
    yield check_predict_proba_raises, FactorizationMachineClassifier
    yield check_predict_proba_raises, PolynomialNetworkClassifier


def check_loss_raises(Clf):
    """Test error on unsupported loss"""
    clf = Clf(loss='hinge', random_state=0)
    assert_raises(ValueError, clf.fit, X, y)


def test_loss_raises():
    yield check_loss_raises, FactorizationMachineClassifier
    yield check_loss_raises, PolynomialNetworkClassifier


def check_clf_multiclass_error(Clf):
    """Test that classifier raises TypeError on multiclass/multilabel y"""
    y_ = np.column_stack([y, y])
    clf = Clf(random_state=0)
    assert_raises(TypeError, clf.fit, X, y_)


def test_clf_multiclass_error():
    yield check_clf_multiclass_error, FactorizationMachineClassifier
    yield check_clf_multiclass_error, PolynomialNetworkClassifier


def check_clf_float_error(Clf):
    """Test that classifier raises TypeError on multiclass/multilabel y"""
    y_ = [0.1, 0.2, 0.3, 0.4]
    clf = Clf(random_state=0)
    assert_raises(TypeError, clf.fit, X, y_)


def test_clf_float_error():
    yield check_clf_float_error, FactorizationMachineClassifier
    yield check_clf_float_error, PolynomialNetworkClassifier


def check_not_fitted(Est):
    est = Est()
    assert_raises_regex(ValueError, "fitted", est.predict, X)


def test_not_fitted():
    yield check_not_fitted, FactorizationMachineClassifier
    yield check_not_fitted, PolynomialNetworkClassifier
    yield check_not_fitted, FactorizationMachineRegressor
    yield check_not_fitted, PolynomialNetworkRegressor


def test_augment():
    # The following linear separable dataset cannot be modeled with just an FM
    X_evil = np.array([[-1, -1], [1, 1]])
    y_evil = np.array([-1, 1])
    clf = FactorizationMachineClassifier(fit_linear=None, fit_lower=None,
                                         random_state=0)
    clf.fit(X_evil, y_evil)
    assert_equal(0.5, clf.score(X_evil, y_evil))

    # However, by adding a dummy feature (a column of all ones), the linear
    # effect can be captured.
    clf = FactorizationMachineClassifier(fit_linear='augment',
                                         fit_lower='augment', random_state=0)
    clf.fit(X_evil, y_evil)
    assert_equal(1.0, clf.score(X_evil, y_evil))
