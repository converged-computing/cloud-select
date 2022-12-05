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

% This prevents errors saying atoms not defined anywhere
#defined instance/2.
#defined instance_attr/4.
#defined has_attr/4.
#defined attr/1.
