# -*- coding: utf-8 -*-

"""
The Local version of the app.
"""

import base64
import io
import os
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import cv2
from PIL import Image
from io import BytesIO


def input_field(title, state_id, state_value, state_max, state_min):
    """Takes as parameter the title, state, default value and range of an input field, and output a Div object with
    the given specifications."""
    return html.Div([
        html.P(title,
               style={
                   'display': 'inline-block',
                   'verticalAlign': 'mid',
                   'marginRight': '5px',
                   'margin-bottom': '0px',
                   'margin-top': '0px'
               }),

        html.Div([
            dcc.Input(
                id=state_id,
                type='number',
                value=state_value,
                max=state_max,
                min=state_min,
                size=7
            )
        ],
            style={
                'display': 'inline-block',
                'margin-top': '0px',
                'margin-bottom': '0px'
            }
        )
    ]
    )
def merge(a, b):
    return dict(a, **b)

def numpy_to_b64(array, scalar=False):
    # Convert from 0-1 to 0-255
    if scalar:
        array = np.uint8(255 * array)

    im_pil = Image.fromarray(array)
    buff = BytesIO()
    im_pil.save(buff, format="png")
    im_b64 = base64.b64encode(buff.getvalue()).decode("utf-8")

    return im_b64

def omit(omitted_keys, d):
    return {k: v for k, v in d.items() if k not in omitted_keys}

def Card(children, **kwargs):
    return html.Section(
        children,
        style=merge({
            'padding': 20,
            'margin': 5,
            'borderRadius': 5,
            'border': 'thin lightgrey solid',

            # Remove possibility to select the text for better UX
            'user-select': 'none',
            '-moz-user-select': 'none',
            '-webkit-user-select': 'none',
            '-ms-user-select': 'none'
        }, kwargs.get('style', {})),
        **omit(['style'], kwargs)
    )

# Generate the default scatter plot
tsne_df = pd.read_csv("data/tsne_3d.csv", index_col=0)

data = []

for idx, val in tsne_df.groupby(tsne_df.index):
    idx = int(idx)

    scatter = go.Scatter3d(
        name=f"Digit {idx}",
        x=val['x'],
        y=val['y'],
        z=val['z'],
        mode='markers',
        marker=dict(
            size=2.5,
            symbol='circle-dot'
        )
    )
    data.append(scatter)


# Layout for the t-SNE graph
tsne_layout = go.Layout(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    )
)

local_layout = html.Div([
    # In-browser storage of global variables
    html.Div(
        id="data-df-and-message",
        style={'display': 'none'}
    ),

    html.Div(
        id="label-df-and-message",
        style={'display': 'none'}
    ),

    html.Div(
        id="images-df-and-message",
        style={'display': 'none'}
    ),
    # Main app
    html.Div([
        html.H2(
            't-SNE Explorer',
            id='title',
            style={
                'float': 'left',
                'margin-top': '20px',
                'margin-bottom': '0',
                'margin-left': '7px'
            }
        ),
        html.Img(
            src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
            style={
                'height': '100px',
                'float': 'right'
            }
        )
    ],
        className="row"
    ),

    html.Div([
        html.Div([
            # Data about the graph
            html.Div(
                id="kl-divergence",
                style={'display': 'none'}
            ),

            html.Div(
                id="end-time",
                style={'display': 'none'}
            ),

            html.Div(
                id="error-message",
                style={'display': 'none'}
            ),

            # The graph
            dcc.Graph(
                id='tsne-3d-plot',
                figure={
                    'data': data,
                    'layout': tsne_layout
                },
                style={
                    'height': '80vh',
                },
            )
        ],
            id="plot-div",
            className="eight columns"
        ),

        html.Div([

            html.H4(
                't-SNE Parameters',
                id='tsne_h4'
            ),

            input_field("Perplexity:", "perplexity-state", 20, 50, 5),

            input_field("Number of Iterations:", "n-iter-state", 400, 1000, 250),

            input_field("Learning Rate:", "lr-state", 200, 1000, 10),

            input_field("Initial PCA dimensions:", "pca-state", 30, 10000, 3),

            html.Button(
                id='tsne-train-button',
                n_clicks=0,
                children='Start Training t-SNE'
            ),

            dcc.Upload(
                id='upload-data',
                children=html.A('Upload your input data here.'),
                style={
                    'height': '45px',
                    'line-height': '45px',
                    'border-width': '1px',
                    'border-style': 'dashed',
                    'border-radius': '5px',
                    'text-align': 'center',
                    'margin-top': '5px',
                    'margin-bottom': '5 px'
                },
                multiple=False,
                max_size=-1
            ),

            dcc.Upload(
                id='upload-label',
                children=html.A('Upload your labels here.'),
                style={
                    'height': '45px',
                    'line-height': '45px',
                    'border-width': '1px',
                    'border-style': 'dashed',
                    'border-radius': '5px',
                    'text-align': 'center',
                    'margin-top': '5px',
                    'margin-bottom': '5px'
                },
                multiple=False,
                max_size=-1
            ),

            dcc.Upload(
                id='upload-images',
                children=html.A('Upload your images csv here.'),
                style={
                    'height': '45px',
                    'line-height': '45px',
                    'border-width': '1px',
                    'border-style': 'dashed',
                    'border-radius': '5px',
                    'text-align': 'center',
                    'margin-top': '5px',
                    'margin-bottom': '5px'
                },
                multiple=False,
                max_size=-1
            ),

            html.Div([
                html.P(id='upload-data-message',
                       style={
                           'margin-bottom': '0px'
                       }),

                html.P(id='upload-label-message',
                       style={
                           'margin-bottom': '0px'
                       }),

                html.P(id='upload-images-message',
                       style={
                           'margin-bottom': '0px'
                       }),

                html.Div(id='training-status-message',
                         style={
                             'margin-bottom': '0px',
                             'margin-top': '0px'
                         }),

                html.P(id='error-status-message')
            ],
                id='output-messages',
                style={
                    'margin-bottom': '2px',
                    'margin-top': '2px'
                }
            ),
            Card(style={'padding': '5px'}, children=[
                    html.Div(id='div-plot-click-message',
                             style={'text-align': 'center',
                                    'margin-bottom': '7px',
                                    'font-weight': 'bold'}
                             ),

                    html.Div(id='div-plot-click-image'),

                    html.Div(id='div-plot-click-wordemb')
                ])
        ],
            className="four columns",
            style={
                'padding': 20,
                'margin': 5,
                'borderRadius': 5,
                'border': 'thin lightgrey solid',

                # Remove possibility to select the text for better UX
                'user-select': 'none',
                '-moz-user-select': 'none',
                '-webkit-user-select': 'none',
                '-ms-user-select': 'none'
            }
        )
    ],
        className="row"
    ),

    html.Div([
        dcc.Markdown('''
This is the local version of the t-SNE explorer. To view the source code, please visit the 
[GitHub Repository](https://github.com/plotly/dash-tsne). 
To view pre-generated simulations of t-SNE, check out the [demo app](https://dash-tsne.herokuapp.com). 
''')],
        style={
            'margin-top': '15px'
        },
        className="row"
    )
],
    className="container",
    style={
        'width': '90%',
        'max-width': 'none',
        'font-size': '1.5rem'
    }
)


def local_callbacks(app):
    def parse_content(contents, filename):
        """This function parses the raw content and the file names, and returns the dataframe containing the data, as well
        as the message displaying whether it was successfully parsed or not."""

        if contents is None:
            return None, ""

        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)

        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))

            else:
                return None, 'The file uploaded is invalid.'
        except Exception as e:
            print(e)
            return None, 'There was an error processing this file.'

        return df, f'{filename} successfully processed.'

    # Uploaded data --> Hidden Data Div
    @app.callback(Output('data-df-and-message', 'children'),
                  [Input('upload-data', 'contents'),
                   Input('upload-data', 'filename')])
    def parse_data(contents, filename):
        data_df, message = parse_content(contents, filename)

        if data_df is None:
            return [None, message]

        elif data_df.shape[1] < 3:
            return [None, f'The dimensions of {filename} are invalid.']

        return [data_df.to_json(orient="split"), message]

    # Uploaded labels --> Hidden Label div
    @app.callback(Output('label-df-and-message', 'children'),
                  [Input('upload-label', 'contents'),
                   Input('upload-label', 'filename')])
    def parse_label(contents, filename):
        label_df, message = parse_content(contents, filename)

        if label_df is None:
            return [None, message]

        elif label_df.shape[1] != 1:
            return [None, f'The dimensions of {filename} are invalid.']

        return [label_df.to_json(orient="split"), message]

    @app.callback(Output('images-df-and-message', 'children'),
                  [Input('upload-images', 'contents'),
                   Input('upload-images', 'filename')])
    def parse_images(contents, filename):
        images_df, message = parse_content(contents, filename)

        if images_df is None:
            return [None, message]

        # elif label_df.shape[1] != 1:
        #     return [None, f'The dimensions of {filename} are invalid.']

        return [images_df.to_json(orient="split"), message]

    # Hidden Data Div --> Display upload status message (Data)
    @app.callback(Output('upload-data-message', 'children'),
                  [Input('data-df-and-message', 'children')])
    def output_upload_status_data(data):
        return data[1]

    # Hidden Label Div --> Display upload status message (Labels)
    @app.callback(Output('upload-label-message', 'children'),
                  [Input('label-df-and-message', 'children')])
    def output_upload_status_label(data):
        return data[1]

    @app.callback(Output('upload-images-message', 'children'),
                  [Input('images-df-and-message', 'children')])
    def output_upload_status_images(data):
        return data[1]

    # Button Click --> Update graph with states
    @app.callback(Output('plot-div', 'children'),
                  [Input('tsne-train-button', 'n_clicks')],
                  [State('perplexity-state', 'value'),
                   State('n-iter-state', 'value'),
                   State('lr-state', 'value'),
                   State('pca-state', 'value'),
                   State('data-df-and-message', 'children'),
                   State('label-df-and-message', 'children')
                   ])
    def update_graph(n_clicks, perplexity, n_iter, learning_rate, pca_dim, data_div, label_div):
        """Run the t-SNE algorithm upon clicking the training button"""

        error_message = None  # No error message at the beginning

        # Fix for startup POST
        if n_clicks <= 0 or data_div is None or label_div is None:
            global data
            kl_divergence, end_time = None, None

        else:
            # Extract the data dataframe and the labels dataframe from the divs. they are both the first child of the div,
            # and are serialized in json
            data_df = pd.read_json(data_div[0], orient="split")
            label_df = pd.read_json(label_div[0], orient="split")

            # Fix the range of possible values
            if n_iter > 1000:
                n_iter = 1000
            elif n_iter < 250:
                n_iter = 250

            if perplexity > 50:
                perplexity = 50
            elif perplexity < 5:
                perplexity = 5

            if learning_rate > 1000:
                learning_rate = 1000
            elif learning_rate < 10:
                learning_rate = 10

            if pca_dim > data_df.shape[1]:  # We limit the pca_dim to the dimensionality of the dataset
                pca_dim = data_df.shape[1]
            elif pca_dim < 3:
                pca_dim = 3

            # Start timer
            start_time = time.time()

            # Apply PCA on the data first
            pca = PCA(n_components=pca_dim)
            data_pca = pca.fit_transform(data_df)

            # Then, apply t-SNE with the input parameters
            tsne = TSNE(n_components=3,
                        perplexity=perplexity,
                        learning_rate=learning_rate,
                        n_iter=n_iter)

            try:
                data_tsne = tsne.fit_transform(data_pca)
                kl_divergence = tsne.kl_divergence_

                # Combine the reduced t-sne data with its label
                tsne_data_df = pd.DataFrame(data_tsne, columns=['x', 'y', 'z'])

                label_df.columns = ['label']

                combined_df = tsne_data_df.join(label_df)

                data = []

                # Group by the values of the label
                for idx, val in combined_df.groupby('label'):
                # for idx, val in combined_df.iterrows():
                    # print(idx, val)
                    scatter = go.Scatter3d(
                        name=idx,
                        x=val['x'],
                        y=val['y'],
                        z=val['z'],
                        mode='markers',
                        marker=dict(
                            size=2.5,
                            symbol='circle-dot'
                        )
                    )
                    data.append(scatter)

                end_time = time.time() - start_time

            # Catches Heroku server timeout
            except:
                error_message = "We were unable to train the t-SNE model due to timeout. Try to run it again, or to clone the repo and run the program locally."
                kl_divergence, end_time = None, None

        return [
            # Data about the graph
            html.Div([
                kl_divergence
            ],
                id="kl-divergence",
                style={'display': 'none'}
            ),

            html.Div([
                end_time
            ],
                id="end-time",
                style={'display': 'none'}
            ),

            html.Div([
                error_message
            ],
                id="error-message",
                style={'display': 'none'}
            ),

            # The graph
            dcc.Graph(
                id='tsne-3d-plot',
                figure={
                    'data': data,
                    'layout': tsne_layout
                },
                style={
                    'height': '80vh',
                },
            )
        ]

    # Updated graph --> Training status message
    @app.callback(Output('training-status-message', 'children'),
                  [Input('end-time', 'children'),
                   Input('kl-divergence', 'children')])
    def update_training_info(end_time, kl_divergence):
        # If an error message was output during the training.

        if end_time is None or kl_divergence is None or end_time[0] is None or kl_divergence[0] is None:
            return None
        else:
            end_time = end_time[0]
            kl_divergence = kl_divergence[0]

            return [
                html.P(f"t-SNE trained in {end_time:.2f} seconds.",
                       style={'margin-bottom': '0px'}),
                html.P(f"Final KL-Divergence: {kl_divergence:.2f}",
                       style={'margin-bottom': '0px'})
            ]

    @app.callback(Output('error-status-message', 'children'),
                  [Input('error-message', 'children')])
    def show_error_message(error_message):
        if error_message is not None:
            return [
                html.P(error_message[0])
            ]

        else:
            return []

    @app.callback(Output('div-plot-click-image', 'children'),
                  [Input('tsne-3d-plot', 'clickData')],
                  [State('images-df-and-message', 'children')])
    def display_click_image(clickData, images_div):
        if clickData:
            # Load the same dataset as the one displayed
            # path = f'demo_embeddings/{dataset}/iterations_{iterations}/perplexity_{perplexity}/pca_{pca_dim}/learning_rate_{learning_rate}'

            # try:
            #     embedding_df = pd.read_csv(path + f'/data.csv', encoding="ISO-8859-1")

            # except FileNotFoundError as error:
            #     print(error, "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py")
            #     return



            # Convert the point clicked into float64 numpy array
            click_point_np = np.array([clickData['points'][0][i] for i in ['x', 'y', 'z']]).astype(np.float64)
            scatter = data[-1]
            flag = False
            # print(scatter.ids[0])
            for scatter in data:
                indices = scatter.x.index
                for i, ind in enumerate(indices):
                    point_np = np.array([scatter.x.iloc[i], scatter.y.iloc[i], scatter.z.iloc[i]])
                    if np.all(click_point_np == point_np):
                        flag = True
                        break
                if flag:
                    break

            if flag:
                clicked_idx = ind
                print(clicked_idx)
            # print(dir(scatter))
            # print(scatter.ids)
            # print(scatter.x.index)
            # print(len(data))
            # # Create a boolean mask of the point clicked, truth value exists at only one row
            # # bool_mask_click = tsne_data_df.loc[:, 'x':'z'].eq(click_point_np).all(axis=1)
            # # Retrieve the index of the point clicked, given it is present in the set
            # bool_mask_click = np.array([False])
            # if bool_mask_click.any():
                # clicked_idx = tsne_data_df[bool_mask_click].index[0]
                images_df = pd.read_json(images_div[0], orient="split")
                # print(images_df)
                # Retrieve the image corresponding to the index
                image_path = images_df[0].iloc[clicked_idx]
                print(str(image_path))
                image_np = cv2.imread(str(image_path))
                # if dataset == 'cifar_gray_3000':
                #     image_np = image_vector.values.reshape(32, 32).astype(np.float64)
                # else:
                #     image_np = image_vector.values.reshape(28, 28).astype(np.float64)

                # # Encode image into base 64
                image_b64 = numpy_to_b64(image_np[...,::-1])

                return html.Img(
                    src='data:image/png;base64, ' + image_b64,
                    style={
                        'height': '25vh',
                        'display': 'block',
                        'margin': 'auto'
                    }
                )
        return None
