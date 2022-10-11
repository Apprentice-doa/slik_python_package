import sys
import docs
import paths

from io import StringIO

from slik_wrangler import loadfile

import streamlit as st
from streamlit.scriptrunner import script_run_context

from threading import current_thread
from contextlib import contextmanager


# Hidden Functions
def _convert_to_html(opt):
    text = opt[1: opt.index(']')]
    link = opt[opt.index('(') + 1: opt.index(')')]

    return f"<b><a href='{link}' style='color: #fff'>{text}</a></b>"


def _divider():
    """
    Sub-routine to create a divider for webpage contents
    """

    st.markdown("""---""")


# Non Hidden Functions
def app_section_button(*options):
    """
    Code Inspiration: https://github.com/soft-nougat/dqw-ivves

    Navigation bar for the site application

    :param options: collection of markdown styled links
                    to place in navigation bar.
                    Maximum of 4 and minimum of 2 allowed
    """

    options = tuple(map(_convert_to_html, options))

    def call_col(col_1, col_2, col_3=None, col_4=None):
        for i, col in enumerate((col_1, col_2, col_3, col_4)):
            if col is not None:
                with col:
                    st.markdown(options[i], unsafe_allow_html=True)

    options_len = len(options)
    col1 = col2 = col3 = col4 = None

    if options_len in range(2, 5):
        if options_len == 2:
            col1, col2 = st.columns(2)
        elif options_len == 3:
            col1, col2, col3 = st.columns(3)
        elif options_len == 4:
            col1, col2, col3, col4 = st.columns(4)
    else:
        raise ValueError(f"Max column should be 4 and Min column 2! {options_len} given.")

    call_col(col1, col2, col3, col4)


def app_meta():
    """
    Adds app meta data to web applications
    """

    # Set website details
    st.set_page_config(
        page_title="Slik-Wrangler",
        page_icon=paths.SITE_LOGO_PATH,
        layout='centered'
    )


@st.cache
def convert_df(dataframe):
    """
    IMPORTANT: Cache the conversion to prevent computation on every rerun
    """

    return dataframe.to_csv().encode('utf-8')


def display_app_header(main_txt, sub_txt, is_sidebar=False):
    """
    Code Credit: https://github.com/soft-nougat/dqw-ivves

    function to display major headers at user interface
    :param main_txt: the major text to be displayed
    :param sub_txt: the minor text to be displayed
    :param is_sidebar: check if its side panel or major panel
    :return:
    """

    html_temp = f"""
    <h2 style = "text_align:center; font-weight: bold;"> {main_txt} </h2>
    <p style = "text_align:center;"> {sub_txt} </p>
    </div>
    """

    if is_sidebar:
        st.sidebar.markdown(html_temp, unsafe_allow_html=True)
    else:
        st.markdown(html_temp, unsafe_allow_html=True)


def display_sidebar_url_log(_docs, _urls):
    for _doc, _url in zip(_docs, _urls):
        st.write(_doc)
        st.markdown(
            _convert_to_html(_url),
            unsafe_allow_html=True
        )
        _divider()


@contextmanager
def st_redirect(src, dst, how=None):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)
    s = []

    with StringIO() as buffer:
        old_write = src.write

        #script_run_context
        def new_write(b):
            if getattr(current_thread(), script_run_context.SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                buffer.write(b)
                value = buffer.getvalue()
                s.append(value)
                if not how:
                    output_func(value)
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write

    if how == 'json':
        st.json(s[0])


@contextmanager
def st_stdout(dst, how=None):
    with st_redirect(sys.stdout, dst, how):
        yield


@st.cache(allow_output_mutation=True)
def load_data(file):
    """
    Loads file using slik-wrangler _read_file api and caches it
    using the streamlit caching

    :param file: st.uploader file object
    """

    return loadfile._read_file(file)


class Executor:
    """
    Master class for managing all function operations
    """

    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.operations = []
        self.functions = []
        self.transformation_func_param = []
        self.transformed_df = self.dataframe

    def add_operation(self, operation, function):
        self.operations.append(operation)
        self.functions.append(function)

    def execute(self):
        for opr, func in zip(self.operations, self.functions):
            print("Hello")
            if opr:
                if func is not None:
                    try:
                        evaluation_results = func(self.transformed_df)
                        print("help(func)")
                        self.transformation_func_param.append(evaluation_results)

                        if evaluation_results:
                            self.transformed_df = evaluation_results[0](**evaluation_results[1])
                            print("Even Got Here!!!!!")

                        print(evaluation_results, self.transformed_df)
                    except:
                        docs.section_not_available(
                            message="Function appears to be faulty! "
                                    "Please review it's entry level parameters",
                            add_plain_image=True
                        )
                else:
                    docs.section_not_available(add_plain_image=True)


