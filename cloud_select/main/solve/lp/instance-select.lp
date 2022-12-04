%============================================================================
% Cloud Select Solver
%============================================================================

%----------------------------------------------------------------------------
% Cloud Instances
%----------------------------------------------------------------------------

% Select a cloud instance with a matching (exact) attribute
has_attr(Cloud, Instance, Attribute, Value) :-
    attr(Attribute),
    instance_attr(Cloud, Instance, InstanceAttr, InstanceValue),
    InstanceValue = Value,
    InstanceAttr = Attribute.
