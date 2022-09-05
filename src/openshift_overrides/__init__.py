from openshift.result import Result
from openshift import oc_action
import logging


def modify_and_apply(apiobj, modifier_func, retries=2, cmd_args=None):
    """
    Calls the modifier_func with apiobj. The function should modify the model of the apiobj argument
    and return True if it wants this method to try to apply the change via the API. For robust
    implementations, a non-zero number of retries is recommended.

    :param modifier_func: Called before each attempt with an apiobj. The associated model will be refreshed before
        each call if necessary. If the function finds changes it wants to make to the model, it should
        make them directly and return True. If it does not want to make changes, it should return False.
    :param cmd_args: An optional list of additional arguments to pass on the command line
    :param retries: The number of times to retry. A value of 0 means only one attempt will be made.
    :return: A Result object containing a record of all attempts AND a boolean. The boolean indicates
    True if a change was applied to a resource (i.e. it will be False if modifier_func suggested no
    change was necessary by returning False).
    :rtype: Result, bool
    """
    r = Result("apply")

    applied_change = False
    for attempt in reversed(list(range(retries + 1))):

        do_apply = modifier_func(apiobj)

        # Modifier does not want to modify this object -- stop retrying. Retuning None should continue attempts.
        if do_apply is False:
            break

        apply_action = oc_action(apiobj.context, "apply", cmd_args=["-f", "-", cmd_args],
                                    namespace=apiobj.namespace(if_missing=None), stdin_obj=apiobj.as_dict(),
                                    last_attempt=(attempt == 0))

        r.add_action(apply_action)

        if apply_action.status == 0:
            applied_change = True
            break
        else:
            if (apiobj.kind() == 'deployment' and 
                'MatchExpressions:[]v1.LabelSelectorRequirement(nil)}: field is immutable' in r.err()):
                # Invalid config: deployment's spec.selector is immutable
                logging.error(f'{apiobj.kind()}/{apiobj.name()} spec.selector is immutable: {r.err().strip()}')
                break
            else:
                # Continue retrying
                pass

        if attempt != 0:
            # Get a fresh copy of the API object from the server
            apiobj.refresh()

    return r, applied_change



    # Conditions
    # - validation error (like immutable spec.selector)
    # - unchanged
    # - successful apply