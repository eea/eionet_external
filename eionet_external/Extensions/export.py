import simplejson as json

meta_attributes = {
    'SerisFolder': ('id', 'title', 'description', 'title_SERIS_home',
        'Eurasia_map_country_list', 'languages', 'map_server_url', 'map_color',
        'reasons_block_link', '__ac_local_roles__', '__ac_roles__', '_owner',
        '_Manage_properties_Permission', '_Delete_objects_Permission',
        '_Copy_or_Move_Permission', '_Add_SoEReports_Permission',
        '_Add_SERIS_Coverages_Permission'),
    'SERIS Coverage': ('id', 'title', 'coverage_type', 'index_code',
                     'ISO_code', '__ac_local_roles__', ),
    'SoEReport': ('id', '__ac_local_roles__', 'title', 'creation_date',
        'description', 'identifier', 'coverage_year_start', 'language',
        'rights','source', 'block_link', 'translated', 'title_English',
        'reason_block_link', 'source_identifier', 'block_source_link',
        'category', 'SpatialCoverage_terms', ),
}

def rec(context):
    data = {'meta_type': context.meta_type}
    for k, v in context.__dict__.iteritems():
        if k in meta_attributes[context.meta_type]:
            try: #Check if the value is serializable
                json.dumps(v)
                data[k] = v
            except:
                data[k] = unicode(v)
    if hasattr(context, 'objectValues'):
        for ob in context.objectValues(meta_attributes.keys()):
            if '__children__' not in data:
                data['__children__'] = []
            data['__children__'].append(rec(ob))
    return data

def export_json(self):
    if self.meta_type == 'SerisFolder':
        return json.dumps(rec(self), indent=4)
    return ''
