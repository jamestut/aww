#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <sys/sysctl.h>
#include <libproc.h>

PyObject * get_procs(PyObject * self);

PyMethodDef nativeapi_funcs[] = {
	{
		"get_procs",
		(PyCFunction)get_procs,
		METH_NOARGS,
		"Get process list on macOS."
	},
	{NULL}
};

PyModuleDef nativeapi_mod = {
	PyModuleDef_HEAD_INIT,
	"nativeapi",
	"Module to access macOS APIs",
	-1,
	nativeapi_funcs,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC PyInit_nativeapi(void) {
	return PyModule_Create(&nativeapi_mod);
}

PyObject * get_procs(PyObject * self) {
	PyObject * ret = NULL;
	struct kinfo_proc * kpi = NULL;
	char * procpathbuff = NULL;

	int mib[4] = { CTL_KERN, KERN_PROC, KERN_PROC_ALL, 0 };
	size_t buffer_size = 0;
	if (sysctl(mib, 4, NULL, &buffer_size, NULL, 0) < 0) {
		PyErr_SetFromErrno(PyExc_OSError);
		goto finish;
	}
	kpi = malloc(buffer_size);
	if (!kpi) {
		PyErr_SetFromErrno(PyExc_OSError);
		goto finish;
	}
	if (sysctl(mib, 4, kpi, &buffer_size, NULL, 0) < 0) {
		PyErr_SetFromErrno(PyExc_OSError);
		goto finish;
	}

	if (buffer_size % sizeof(struct kinfo_proc)) {
		PyErr_SetString(PyExc_RuntimeError, "Userland out of sync with kernel");
		goto finish;
	}

	size_t nprocs = buffer_size / sizeof(struct kinfo_proc);

	procpathbuff = malloc(PROC_PIDPATHINFO_MAXSIZE);
	if (!procpathbuff) {
		PyErr_SetFromErrno(PyExc_OSError);
		goto finish;
	}

	ret = PyList_New(nprocs);
	if (!ret) {
		PyErr_SetString(PyExc_RuntimeError, "Error creating new list");
		goto finish;
	}

	for (size_t i = 0; i < nprocs; ++i) {
		pid_t pid = kpi[i].kp_proc.p_pid; // save
		int pathlen = proc_pidpath(pid, procpathbuff, PROC_PIDPATHINFO_MAXSIZE);
		PyObject * pypath = Py_None;
		if (pathlen > 0) {
			pypath = PyUnicode_FromKindAndData(
				PyUnicode_1BYTE_KIND, procpathbuff, pathlen);
		}
		PyObject * tpl = PyTuple_Pack(3,
			PyLong_FromLong(pid),
			pypath,
			PyLong_FromLong(kpi[i].kp_proc.p_stat));
		PyList_SET_ITEM(ret, i, tpl);
	}

finish:
	if (kpi)
		free(kpi);
	if (procpathbuff)
		free(procpathbuff);
	return ret;
}
