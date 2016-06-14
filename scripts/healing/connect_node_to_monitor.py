from cloudify import ctx

host_id = ctx.target.node.properties['resource_id']
nodes_to_monitor = ctx.source.instance.runtime_properties.get('nodes_to_monitor', [])
nodes_to_monitor.append(host_id)
ctx.source.instance.runtime_properties['nodes_to_monitor'] = nodes_to_monitor
