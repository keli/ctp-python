%module(directors="1") ctp

%include "typemaps.i"

//%begin %{
//#define SWIG_PYTHON_STRICT_BYTE_CHAR
//%}

// #define %ctp_new_instance(TYPE...) %reinterpret_cast(calloc(1, sizeof(TYPE)), TYPE*)
// #define %ctp_new_copy(VAL, TYPE...) %reinterpret_cast(memcpy(%ctp_new_instance(TYPE), &(VAL), sizeof(TYPE)), TYPE*)

// %extend TAGNAME {
//   struct TAGNAME *__copy__() {
//     return %ctp_new_copy(*$self, struct TAGNAME);
//   }
// }

%pythonbegin %{
from sys import stderr, float_info
from traceback import print_exc, print_exception
%}

%pythoncode %{
def _swig_repr(self):
    values = []
    for k in vars(self.__class__):
        if not k.startswith('_'):
            v = getattr(self, k)
            if isinstance(v, float):
                if v == float_info.max:
                    values.append("%s: None" % k)
                else:
                    values.append("%s: %.2f" % (k, v))
            elif isinstance(v, int):
                values.append("%s: %i" % (k, v))
            else:
                values.append('%s: "%s"' % (k, v))

    return "<%s.%s; %s>" % (self.__class__.__module__, self.__class__.__name__, ', '.join(values))
%}

%{
#define SWIG_FILE_WITH_INIT
#include "ThostFtdcUserApiDataType.h"
#include "ThostFtdcUserApiStruct.h"
#include "ThostFtdcMdApi.h"
#include "ThostFtdcTraderApi.h"
#include "iconv.h"
%}

%feature("director:except") {
    if ($error != NULL) {

        if ( !( PyErr_ExceptionMatches(PyExc_SystemExit) ||
                PyErr_ExceptionMatches(PyExc_SystemError) ||
                PyErr_ExceptionMatches(PyExc_KeyboardInterrupt) ) )
        {
            PyObject *value = 0;
            PyObject *traceback = 0;

            PyErr_Fetch(&$error, &value, &traceback);
            PyErr_NormalizeException(&$error, &value, &traceback);

            {
                if (value == NULL) {
                    value = Py_None;
                }
                if (traceback == NULL) {
                    traceback = Py_None;
                }
                swig::SwigVar_PyObject swig_method_name = SWIG_Python_str_FromChar((char *) "pyError");
                swig::SwigVar_PyObject result = PyObject_CallMethodObjArgs(swig_get_self(), (PyObject *) swig_method_name, $error, value, traceback, NULL);
            }

            Py_XDECREF($error);
            Py_XDECREF(value);
            Py_XDECREF(traceback);

            $error = PyErr_Occurred();
            if ($error != NULL) {
                PyErr_Print();
                throw Swig::DirectorMethodException();
            }
        }
        else
        {
            throw Swig::DirectorMethodException();
        }
    }
}

%extend CThostFtdcMdSpi {
%pythoncode {
    def pyError(self, type, value, traceback):
        '''Handles an error thrown during invocation of an method.

        Arguments are those provided by sys.exc_info()
        '''
        stderr.write("Exception thrown during method dispatch:\n")
        print_exception(type, value, traceback)
}
}

%extend CThostFtdcTraderSpi {
%pythoncode {
    def pyError(self, type, value, traceback):
        '''Handles an error thrown during invocation of an method.

        Arguments are those provided by sys.exc_info()
        '''
        stderr.write("Exception thrown during method dispatch:\n")
        print_exception(type, value, traceback)
}
}

/* Exception handling */
%include exception.i
%exception {
    try {
        $action
    } catch(Swig::DirectorPureVirtualException &e) {
        /* Call to pure virtual method, raise not implemented error */
        PyErr_SetString(PyExc_NotImplementedError, "$decl not implemented");
        SWIG_fail;
    } catch(Swig::DirectorException &e) {
        /* Fail if there is a problem in the director proxy transport */
        SWIG_fail;
    } catch(std::exception& e) {
        /* Convert standard error to Exception */
        PyErr_SetString(PyExc_Exception, const_cast<char*>(e.what()));
        SWIG_fail;
    } catch(...) {
        /* Final catch all, results in runtime error */
        PyErr_SetString(PyExc_RuntimeError, "Unknown error caught in CTP SWIG wrapper...");
        SWIG_fail;
    }
}

%typemap(out) char[ANY], char[] {
    if ($1) {
        size_t inlen = strlen($1);
        if (inlen == 0) {
            $result = SWIG_FromCharPtr("");
        } else {
            iconv_t conv = iconv_open("UTF-8", "GBK");
            if (conv == (iconv_t)-1) {
                $result = SWIG_FromCharPtr($1);
                if (PyErr_WarnEx(PyExc_UnicodeWarning, "Failed to initialize iconv.", 1) < 0) {
                    return NULL;
                }
            } else {
                size_t outlen = 4096;
                char buf[4096];
                char **in = &$1;
                char *out = buf;

                if (iconv(conv, in, &inlen, &out, &outlen) != (size_t)-1) {
                    iconv_close(conv);
                    $result = SWIG_FromCharPtrAndSize(buf, sizeof buf - outlen);
                } else {
                    iconv_close(conv);
                    $result = SWIG_FromCharPtr($1);
                    if (PyErr_WarnEx(PyExc_UnicodeWarning, "Failed to convert '$1_name' from GBK to UTF-8.", 1) < 0) {
                        return NULL;
                    }
                }
            }
        }
    }
}

%typemap(in) (char **ARRAY, int SIZE) {
    /* Check if is a list */
    if (PyList_Check($input)) {
        int size = PyList_Size($input);
        int i = 0;
        $1 = (char **) malloc((size+1)*sizeof(char *));
        $2 = size;

        for (i = 0; i < size; i++) {
            PyObject *o = PyList_GetItem($input, i);
            if (PyUnicode_Check(o)) {
                $1[i] = (char *)PyUnicode_AsUTF8(PyList_GetItem($input, i));
                if ($1[i] == NULL) {
                    PyErr_SetString(PyExc_TypeError, "failed to convert UTF-8");
                    SWIG_fail;
                }
            } else {
                free($1);
                PyErr_SetString(PyExc_TypeError, "list must contain strings");
                SWIG_fail;
            }
        }
        $1[i] = 0;
    } else {
        PyErr_SetString(PyExc_TypeError, "not a list");
        SWIG_fail;
    }
}

%typemap(freearg) (char **ARRAY, int SIZE) {
    free((char *)$1);
}

%apply (char **ARRAY, int SIZE) { (char *ppInstrumentID[], int nCount) };

%feature("director") CThostFtdcMdSpi;
%feature("director") CThostFtdcTraderSpi;

// Ignore problematic character constants that cause compilation issues on Windows
%ignore THOST_FTDC_FTC_BankLaunchBankToBroker;
%ignore THOST_FTDC_FTC_BrokerLaunchBankToBroker;
%ignore THOST_FTDC_FTC_BankLaunchBrokerToBank;
%ignore THOST_FTDC_FTC_BrokerLaunchBrokerToBank;

// Additional constants to ignore
%ignore THOST_FTDC_VTC_BankBankToFuture;
%ignore THOST_FTDC_VTC_BankFutureToBank;
%ignore THOST_FTDC_VTC_FutureBankToFuture;
%ignore THOST_FTDC_VTC_FutureFutureToBank;

%include "ThostFtdcUserApiDataType.h"
%include "ThostFtdcUserApiStruct.h"
%include "ThostFtdcMdApi.h"
%include "ThostFtdcTraderApi.h"
