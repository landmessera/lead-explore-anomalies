###########################################################################
# Helper Functions
###########################################################################

def anomaly_ranges(changes, by_cluster):
    anomaly_ranges = []
    for idx, change in enumerate(changes):
        if change[1] == 'increase':
            anomaly_ranges.append((change[0], changes[idx+1][0]))

    return anomaly_ranges

def detect_changes(df, column):
    current = ''
    changes = []

    for ind in df.index:
        if current != df[column][ind]:
            current = df[column][ind]
            changes.append([ind, df[column][ind]])

    return changes

def highlight_cluster(fig, df, changes):
    # Highlight areas according to the cluster values
    for i, val in enumerate(changes):
        if (i + 1) == len(changes):
            changes_last_date = changes[-1][0]
            changes_last_state = changes[-1][1]
            last_date = df.index[-1]
            fig.add_vrect(
                x0=changes_last_date, x1=last_date,
                fillcolor='white', opacity=0.2,
                layer="below", line_width=0)

        else:
            if changes[i][1] == 'increase':
                fig.add_vrect(
                    x0=changes[i][0], x1=changes[i + 1][0],
                    fillcolor='red', opacity=0.2,
                    layer="below", line_width=0)

    fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                      xaxis={'showgrid': False},
                      yaxis={'showgrid': True})
    return fig

def highlight_anomaly(fig, anomaly_range):
    fig.add_vrect(
            x0=anomaly_range[0], x1=anomaly_range[1],
            fillcolor='red', opacity=0.2,
            layer="below", line_width=0)

    fig.update_layout(xaxis_title="Date", yaxis_title="Values",
                      xaxis={'showgrid': False},
                      yaxis={'showgrid': True})
    return fig

def position_legend(fig, show_legend):
    if show_legend:
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
    else:
        fig.update_layout(showlegend=show_legend)
    return fig

def change_labels(fig, sensor_labels_ext):
    try:
        fig.for_each_trace(lambda t: t.update(name=sensor_labels_ext[t.name],
            legendgroup=sensor_labels_ext[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, sensor_labels_ext[t.name])
            )
        )
    except:
        print('Label of sensor not available in sensor name mapping.')

    return fig
