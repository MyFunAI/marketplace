

"""
    Serialize a list of serializable items
    @param items - item to be serialized
    @param serializer - the function which serializes each item
    @return a list of serialized items
"""
def serialize_all(items, serializer):
    return [serializer(item) for item in items]

