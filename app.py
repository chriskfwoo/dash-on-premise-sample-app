import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine
from components import Header, Row


# connect to database
con_string = f"postgresql+pg8000{os.getenv('DATABASE_URL').lstrip('postgres')}"
engine = create_engine(con_string)
connection = engine.connect()

app = dash.Dash(__name__)

# expose the server variable for deployments
server = app.server

# standard Dash app code below
app.layout = html.Div([
    Header("PostgreSQL DEMO APP", app),
    Row([
        html.Div([
            dcc.Textarea(
                id="sql__textarea__input",
                placeholder="Enter a SQL command...",
                value="",
                className="sql__textarea"
            ),
            html.Div([
                html.Button(
                    "Execute query",
                    id="sql__execute__handler",
                    className="sql__button",
                    n_clicks_timestamp=0
                ),
                html.Button(
                    "Reset DB",
                    id="sql__reset__handler",
                    className="sql__button--red",
                    n_clicks_timestamp=0
                ),
            ], className="btn--group")
        ]),
    ]),
    Row([
        html.Div([
            html.H4("Raw query output"),
            html.Pre(
                [""],
                id="sql__output",
                className="sql__pre"
            )
        ]),
    ]),
], className="container")


@app.callback(
    Output("sql__output", "children"),
    [
        Input("sql__execute__handler", "n_clicks_timestamp"),
        Input("sql__reset__handler", "n_clicks_timestamp")
    ],
    [State("sql__textarea__input", "value")]
)
def execute_query(btn_execute, btn_reset, value):

    if value == "" or value is None:
        raise PreventUpdate

    # reset button is clicked
    if int(btn_execute) < int(btn_reset):
        return drop_all_tables()

    # execute button clicked
    return execute_query(value)


def execute_query(statement):
    """ Execute PostgreSQL statement. """

    try:
        result = connection.execute(statement).fetchall()
        print(result)
        return f"Success: \n {result}"
    except Exception as error:
        print(error)
        return f"Error: \n {error}"


def drop_all_tables():
    """ Drops all tables and schema. """

    try:
        first_stmt = connection.execute("DROP SCHEMA public CASCADE;")
        second_stmt = connection.execute("CREATE SCHEMA public;")
        return f"Success: \n {first_stmt} \n {second_stmt}"
    except Exception as error:
        return f"Error: \n {error}"


if __name__ == '__main__':
    app.run_server(debug=True)
