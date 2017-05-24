import logging

from ddfeedback import get_description_of_changes

left_code = 'a + b'
right_code = '(a + b) * c'

logger = logging.getLogger(__name__)

logger.info('\n%s', '\n'.join(get_description_of_changes(left_code, right_code)))
