import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine
from components import Header, Row, Column


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
        Column([
            html.Div([
                dcc.Markdown('''
                    ##### Sample Queries

                    ```
                    CREATE TABLE Persons (
                        PersonID int,
                        LastName varchar(255)
                    );
                    ```

                    ```
                    INSERT INTO Persons (PersonId, LastName)
                    VALUES (1, 'woo');
                    ```

                    ```
                    SELECT * FROM Persons;
                    ```

                    ```
                    DROP TABLE Persons;
                    ```

                ''')
            ]),
        ], width=5),
        Column([
            html.Div([
                html.H5("SQL Editor"),
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
                        n_clicks_timestamp=0,
                        title="awesome"
                    ),
                    html.Button(
                        "Reset DB",
                        id="sql__reset__handler",
                        className="sql__button--red",
                        n_clicks_timestamp=0
                    ),
                ], className="btn--group")
            ]),

        ], width=7),
    ]),
    Row([
        html.Div([
            html.H5("Query Output"),
            html.Pre(
                ["No output."],
                id="sql__output",
                className="sql__pre"
            )
        ]),
        html.Div([
            html.H5("Log History"),
            html.Pre(
                ["No history."],
                id="sql__history__output",
                className="sql__history__pre"
            )
        ], className="mt-2"),
    ]),
    dcc.Store(id="log_storage"),
], className="container")


@app.callback(
    [
        Output("sql__output", "children"),
        Output("sql__history__output", "children"),
        Output("log_storage", "data"),
    ],
    [
        Input("sql__execute__handler", "n_clicks_timestamp"),
        Input("sql__reset__handler", "n_clicks_timestamp")
    ],
    [
        State("sql__textarea__input", "value"),
        State("log_storage", "data")
    ]
)
def execute_query(btn_execute, btn_reset, value, history):

    if value == "" or value is None:
        raise PreventUpdate

    # reset button is clicked
    if int(btn_execute) < int(btn_reset):
        history_storage = add_to_history(int(btn_reset), "DROP TABLES", history)
        return drop_all_tables(), output_history(history_storage), history_storage,

    # execute button clicked
    history_storage = add_to_history(int(btn_execute), value, history)
    return execute_query(value), output_history(history_storage), history_storage


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


def add_to_history(timestamp, statement, history):
    """ Add dictionnary to dcc store. """

    ts = datetime.fromtimestamp(timestamp//1000.0).strftime('%Y-%m-%d %H:%M:%S')
    if history is None:
        history = []
    history.append({
        "ts": ts,
        "statement": statement.replace('\r', '').replace('\n', '')
    })
    return history


def output_history(history):
    """ Format the history logs to output. """

    output = [f"{item['ts']}: {item['statement']}" for item in reversed(history)]
    return "\n".join(output)


if __name__ == '__main__':
    app.run_server(debug=True)
