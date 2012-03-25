def base_template_chooser(request):
    http_host = request.META['HTTP_HOST']
    if http_host == 'admin.data.ox.ac.uk':
        base_template_name = 'hosts/admin.html'
    elif http_host == 'time-series.data.ox.ac.uk':
        base_template_name = 'hosts/timeseries.html'
    else:
        base_template_name = 'hosts/dataox.html'
    return {'base_template_name': base_template_name}
