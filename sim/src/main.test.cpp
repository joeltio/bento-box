#include <string>
#include <gtest/gtest.h>
#include <google/protobuf/util/message_differencer.h>
#include "bento/protos/references.pb.h"

using namespace std;

// test that we can build protobuf messages
TEST(proto, CanBuildProtobufMessage) {
    // build a test proto message to serialise
    bento::protos::AttributeRef attrRef;
    attrRef.set_entity_id(24);
    attrRef.set_component("Sprite2D");
    // serialise to binary string and parsed back into protobuf messsage
    string encoded = attrRef.SerializeAsString();
    bento::protos::AttributeRef restored;
    restored.ParseFromString(encoded);
    google::protobuf::util::MessageDifferencer::Equals(restored, attrRef);
}
