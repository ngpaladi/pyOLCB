import can
import pyolcb
import time

TEST_ADDRESS = '05.01.01.01.8C.00'
TEST_OTHER_ADDRESS = '05.01.01.01.8C.01'
GLOBAL_ADDRESS = '00.00.00.00.00.00'

# For efficiency's sake we initialize the BUS and NODE here so we don't have to re-create every time
BUS = can.Bus(interface='socketcan', channel='vcan0', bitrate=125000, receive_own_messages=True) # Primary Bus
BUS2 = can.Bus(interface='socketcan', channel='vcan0', bitrate=125000, receive_own_messages=True) # Secondary Bus for validating responses
MSGS = [] # List of all messages received
can.Notifier(BUS2, [MSGS.append])
NODE = pyolcb.Node(pyolcb.Address(TEST_ADDRESS), pyolcb.Interface(BUS))

def test_initialize_node():
    """
    Test the :class:`Node` initialization message.
    """
    time.sleep(1)
    assert MSGS[-1].data == bytearray(pyolcb.utilities.process_bytes(6, TEST_ADDRESS))
    assert MSGS[-1].arbitration_id == pyolcb.message_types.Initialization_Complete.get_can_header(NODE.address)

def test_produce_consume_event():
    """
    Test the :class:`Node` event message.
    """

    def event_processor(message:pyolcb.Message = None, *args, **kwargs):
        assert message.data == pyolcb.utilities.process_bytes(8, TEST_ADDRESS+'.00.01')
        assert message.message_type == pyolcb.message_types.Producer_Consumer_Event_Report
        NODE.produce(2)

    NODE.add_consumer(1, event_processor)
    NODE.produce(1)
    time.sleep(1)
    assert MSGS[-1].data == pyolcb.utilities.process_bytes(8, TEST_ADDRESS+'.00.02')
    

def test_verify_node_id_global():
    """
    Test the :class:`Node` global verify node ID message.
    """
    NODE.verify_node_id()
    time.sleep(1)
    assert MSGS[-2].data == bytearray(
        pyolcb.utilities.process_bytes(6, NODE.address.full))
    assert MSGS[-2].arbitration_id == pyolcb.message_types.Verify_Node_ID_Number_Global.get_can_header(NODE.address)


def test_verify_node_id_addressed():
    """
    Test the :class:`Node` addressed verify node ID message.
    """
    test_addr = pyolcb.Address(TEST_OTHER_ADDRESS)
    test_addr.set_alias(TEST_OTHER_ADDRESS[-4:])
    NODE.verify_node_id(test_addr)
    time.sleep(1)
    assert MSGS[-1].data == bytearray(
        pyolcb.utilities.process_bytes(2, TEST_OTHER_ADDRESS[-4:]))
    assert MSGS[-1].arbitration_id == pyolcb.message_types.Verify_Node_ID_Number_Addressed.get_can_header(NODE.address)

    


        

