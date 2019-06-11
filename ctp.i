%module(directors="1") ctp

%include "typemaps.i"

//%begin %{
//#define SWIG_PYTHON_STRICT_BYTE_CHAR
//%}

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
        PyObject *exc, *val, *tb;
        PyErr_Fetch(&exc, &val, &tb);
        PyErr_NormalizeException(&exc, &val, &tb);
        std::string err_msg("In method '$symname': ");

        PyObject* exc_str = PyObject_GetAttrString(exc, "__name__");
        err_msg += PyUnicode_AsUTF8(exc_str);
        Py_XDECREF(exc_str);

        if (val != NULL)
        {
            PyObject* val_str = PyObject_Str(val);
            err_msg += ": ";
            err_msg += PyUnicode_AsUTF8(val_str);
            Py_XDECREF(val_str);
        }

        Py_XDECREF(exc);
        Py_XDECREF(val);
        Py_XDECREF(tb);

        Swig::DirectorMethodException::raise(err_msg.c_str());
    }
}

%typemap(out) char[ANY], char[] {
    if ($1) {
        iconv_t conv = iconv_open("UTF-8", "GBK");
        if (conv == (iconv_t)-1) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to initialize iconv.");
            SWIG_fail;
        } else {
            size_t inlen = strlen($1);
            size_t outlen = inlen * 2;
            char buf[outlen] = {};
            char **in = &$1;
            char *out = buf;

            if (iconv(conv, in, &inlen, &out, &outlen) != (size_t)-1) {
                iconv_close(conv);
                $result = SWIG_FromCharPtrAndSize(buf, sizeof buf - outlen);
            } else {
                iconv_close(conv);
                PyErr_SetString(PyExc_UnicodeError, "Error converting from GBK to UTF-8.");
                SWIG_fail;
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

%include "ThostFtdcUserApiDataType.h"
%include "ThostFtdcUserApiStruct.h"
%include "ThostFtdcMdApi.h"
%include "ThostFtdcTraderApi.h"
