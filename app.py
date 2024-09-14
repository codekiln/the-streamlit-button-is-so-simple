import streamlit as st

TITLE = "The streamlit button is so simple"

st.set_page_config(page_title=TITLE, initial_sidebar_state="auto", menu_items=None)

NUM_RUNS = "num_runs"
NUM_WIDGETS = "num_widgets"

ADD_WIDGET_BUTTON_NAME = "ADD WIDGET"
ADD_WIDGET_CLICKED = "add_widget_clicked"

UNDO_WIDGET_BUTTON_NAME = f"UNDO {ADD_WIDGET_BUTTON_NAME}"
UNDO_WIDGET_CLICKED = "undo_widget_clicked"

KEY_METRICS = [NUM_RUNS, NUM_WIDGETS, ADD_WIDGET_CLICKED, UNDO_WIDGET_CLICKED]

TRANSCRIPT = "transcript"


if NUM_RUNS not in st.session_state:
    st.session_state[NUM_RUNS] = 1
else:
    st.session_state[NUM_RUNS] += 1

if NUM_WIDGETS not in st.session_state:
    st.session_state[NUM_WIDGETS] = 0

if TRANSCRIPT not in st.session_state:
    st.session_state[TRANSCRIPT] = {}


def log(message: dict):
    num_runs = st.session_state[NUM_RUNS]
    num_runs_key = f"num_runs={num_runs}"
    transcript = st.session_state.get(TRANSCRIPT)
    if num_runs_key not in transcript:
        transcript[num_runs_key] = {}
    location = message.pop("location", "no location provided")
    if location in transcript[num_runs_key]:
        raise ValueError(f"Location {location} already exists in transcript")
    transcript[num_runs_key][location] = message
    st.session_state[TRANSCRIPT] = transcript


def print_value_of_add_widget_clicked(
    location_specifier: str, metric_names_list: list[str] | None = None
):
    if metric_names_list is None:
        metric_names_list = KEY_METRICS
    debug_message = {"location": location_specifier}
    for metric_name in metric_names_list:
        debug_message[metric_name] = st.session_state.get(metric_name)
    log(debug_message)


def show_metrics(metric_names_list: list[str] | None = None):
    if metric_names_list is None:
        metric_names_list = KEY_METRICS
    columns = st.columns(len(metric_names_list))
    for i, metric_name in enumerate(metric_names_list):
        with columns[i]:
            st.metric(metric_name, st.session_state.get(metric_name))


st.write(
    f"""
*Conditionally displaying a button based on another button's state is not recommended in Streamlit*

## The set-up
* Clicking the {ADD_WIDGET_BUTTON_NAME} button should add a widget
* If the {ADD_WIDGET_BUTTON_NAME} button is clicked, we should show an {UNDO_WIDGET_BUTTON_NAME} button
* If {UNDO_WIDGET_BUTTON_NAME} button is clicked, it should remove a widget

## The details
* Upon clicking {ADD_WIDGET_BUTTON_NAME}, we set the `{ADD_WIDGET_CLICKED}` session state to True
  and increment the number of widgets in `{NUM_WIDGETS}`.
* If `{ADD_WIDGET_CLICKED}=True` and `{NUM_WIDGETS} > 0`, we show the {UNDO_WIDGET_BUTTON_NAME} button.
* If {UNDO_WIDGET_BUTTON_NAME} is clicked, we decrement the number of widgets in `{NUM_WIDGETS}` and set 
    `{UNDO_WIDGET_CLICKED}` to True.

## Expectation vs reality

### 1 - {UNDO_WIDGET_BUTTON_NAME} doesn't decrement `{NUM_WIDGETS}`
* One might expect the {UNDO_WIDGET_BUTTON_NAME} button to decrement `{NUM_WIDGETS}` if it is clicked, 
  but actually, it doesn't. 

### 2 - According to logging, {UNDO_WIDGET_BUTTON_NAME} wasn't clicked, even though it was
* Look in the transcript for the runs in which you click {UNDO_WIDGET_BUTTON_NAME} to see a 
  `not displaying UNDO ADD WIDGET; ADD WIDGET wasn't clicked` message.
* Also, see the `undo_widget_clicked` metric, which never becomes True.

### 2 - The `{NUM_WIDGETS}` metric is less before then button than after
* One might expect the {NUM_WIDGETS} metric at the top to match the same metric at the bottom, but 
  the metric at the top is 1 less than the one at the bottom.


## Why these things happen (hypothesis)

### 1 - conditioning the render of {UNDO_WIDGET_BUTTON_NAME} on value set in {ADD_WIDGET_BUTTON_NAME} creates a "Bad" situation

This example could be related to (and possibly also logically identical to?) the first "Bad" situation outlined in 
[Button behavior and examples - Streamlit Docs](https://docs.streamlit.io/develop/concepts/design/buttons#when-to-use-if-stbutton):

> **Bad** to nest inside buttons:
> * **Displayed items that should persist as the user continues.**
> * Other widgets which cause the script to rerun when used. 
> * Processes that neither modify session state nor write to a file/database.\* 

### 2 - `{NUM_WIDGETS}` before = 1 - `{NUM_WIDGETS}` after because of top to bottom flow 

Farther down that page, under [Button behavior - A slight problem](https://docs.streamlit.io/develop/concepts/design/buttons#a-slight-problem),
the streamlit docs mention that the value of a button only impacts items below it in the script,
even if session state is updated. 


This example shows how if one stores the boolean value of a button click in session state, 
and then try to use that value to later conditionally display another button, 
the results might not be what you expect.
"""
)


show_metrics()

print_value_of_add_widget_clicked("Before if-else, before initialization")

for button_state_key in [ADD_WIDGET_CLICKED, UNDO_WIDGET_CLICKED]:
    if button_state_key not in st.session_state:
        st.session_state[button_state_key] = False

print_value_of_add_widget_clicked("Before if-else, after initialization")

if st.button(ADD_WIDGET_BUTTON_NAME):
    st.session_state[ADD_WIDGET_CLICKED] = True
    st.session_state[NUM_WIDGETS] += 1
    print_value_of_add_widget_clicked(f"{ADD_WIDGET_BUTTON_NAME} just clicked")
    st.info(f"Number of widgets: {st.session_state[NUM_WIDGETS]}")
else:
    st.session_state[ADD_WIDGET_CLICKED] = False
    print_value_of_add_widget_clicked(f"{ADD_WIDGET_BUTTON_NAME} wasn't clicked")

if num_widgets := st.session_state.get(NUM_WIDGETS):
    if add_widget_clicked := st.session_state.get(ADD_WIDGET_CLICKED):
        if st.button(UNDO_WIDGET_BUTTON_NAME):
            st.session_state[NUM_WIDGETS] = st.session_state[NUM_WIDGETS] - 1
            st.session_state[UNDO_WIDGET_CLICKED] = True
            print_value_of_add_widget_clicked(f"{UNDO_WIDGET_BUTTON_NAME} clicked")
            st.warning(f"Number of widgets: {st.session_state[NUM_WIDGETS]}")
        else:
            st.session_state[UNDO_WIDGET_CLICKED] = False
            print_value_of_add_widget_clicked(
                f"{UNDO_WIDGET_BUTTON_NAME} wasn't clicked"
            )
    else:
        print_value_of_add_widget_clicked(
            f"not displaying {UNDO_WIDGET_BUTTON_NAME}; {ADD_WIDGET_BUTTON_NAME} wasn't clicked"
        )
else:
    print_value_of_add_widget_clicked("no widgets found... no undo button")

print_value_of_add_widget_clicked("After if-else")

with st.expander("Transcript"):
    st.json(st.session_state.get(TRANSCRIPT), expanded=1)

show_metrics()
