import operator
from typing import TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.errors import InvalidUpdateError
from langgraph.graph import StateGraph




class ParentState(TypedDict):
    logs: Annotated[list[str], operator.add]
    result: Annotated[list[str], operator.add]

class FailureLogState(TypedDict):
    logs: Annotated[list[str], operator.add]
    result: Annotated[list[str], operator.add]

class SummarizeLogState(TypedDict):
    logs: Annotated[list[str], operator.add]
    result: Annotated[list[str], operator.add]

### failure graoh
def check_failure(state: FailureLogState):
    print('checking for failure logs')
    failure_report = [log for log in state['logs'] if "ERROR" in log.upper() ]
    return {"result" : [f"found {len(failure_report)} failure logs"]}

failure_graph_builder = StateGraph(FailureLogState)
failure_graph_builder.add_node("check_failure", check_failure)
failure_graph_builder.add_edge(START, "check_failure")
failure_graph_builder.add_edge("check_failure", END)
failure_graph = failure_graph_builder.compile();

### summarize Graph
def summarize_logs(state: SummarizeLogState):
    print('checking to summarize logs ')
    summarize_report = f' total number of logs {len(state["logs"])}'
    return {"result" : [summarize_report]}

summarize_graph_builder = StateGraph(SummarizeLogState)
summarize_graph_builder.add_node("summarize_logs", summarize_logs)
summarize_graph_builder.add_edge(START, "summarize_logs")
summarize_graph_builder.add_edge("summarize_logs", END)
summarize_graph = summarize_graph_builder.compile();

### parent graph
def call_summarize(state: ParentState):
    print('calling summarize graph')
    response = summarize_graph.invoke({"logs": state['raw_logs']})
    return {"result" : [response['summarize_report']]}

def call_failure(state: ParentState):
    print('calling failure graph')
    response = failure_graph.invoke({"logs": state['raw_logs']})
    return {"result" : [response['failure_report']]}

def consolidate_report(state: ParentState):
    print('consolidating report', state['result'])
    # Combine the list into a single clean string
    report_string = " | ".join(state['result'])
    # Return to the NEW key. Since 'final_report' isn't Annotated with add,
    # it just saves this one string.
    return {"final_report": report_string}


parent_builder = StateGraph(ParentState)
parent_builder.add_node("call_failure", failure_graph_builder.compile())
parent_builder.add_node("call_summarize", summarize_graph_builder.compile())
# parent_builder.add_node("consolidate_report", consolidate_report)
parent_builder.add_edge(START, "call_failure")
parent_builder.add_edge(START, "call_summarize")
parent_builder.add_edge(["call_summarize","call_failure"], END)
# parent_builder.add_edge("consolidate_report", END)

parent_graph = parent_builder.compile();





png_data = parent_graph.get_graph(xray=True).draw_mermaid_png()

try:
    result = parent_graph.invoke({"logs":['this is a log with ERROR', 'just simple log', 'another log with EROOR']})
    print(result, result['result'])
except InvalidUpdateError as e:
    print(e)


# Save it to a file in your project folder
with open("graph.png", "wb") as f:
    f.write(png_data)