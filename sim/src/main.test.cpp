#include <string>
#include <gtest/gtest.h>
#include <google/protobuf/util/message_differencer.h>
#include "protos/test.pb.h"

using namespace std;

// temporary test that we can build protobuf messages
TEST(proto, CanBuildProtobufMessage) {
    test::Person person;
    person.set_name("john");
    person.set_age(22);
    // serialise to binary string and parsed back into protobuf messsage
    string encoded = person.SerializeAsString();
    test::Person restored;
    restored.ParseFromString(encoded);
    google::protobuf::util::MessageDifferencer::Equals(restored, person);
}
