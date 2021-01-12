#include <gtest/gtest.h>
#include <core/ics/componentSet.h>
#include <index/entityIndex.h>

#define TEST_SUITE EntityIndex

using namespace ics::index;

TEST(TEST_SUITE, AddAndRemoveCompStoreId) {
    EntityIndex index;
    auto entityId = index.addEntityId();

    ASSERT_EQ(index.getComponents(entityId).size(), 0);
    index.addComponent(entityId, std::pair(1, 1));
    index.addComponent(entityId, std::pair(2, 2));
    index.addComponent(entityId, std::pair(1, 2));
    ASSERT_EQ(index.getComponents(entityId).size(), 3);
    index.removeComponent(entityId, std::pair(1, 1));
    index.removeComponent(entityId, std::pair(2, 2));
    ASSERT_EQ(index.getComponents(entityId).size(), 1);

    auto firstElement = *index.getComponents(entityId).begin();
    ASSERT_EQ(firstElement.first, 1);
    ASSERT_EQ(firstElement.second, 2);
}

TEST(TEST_SUITE, AddMultipleEntities) {
    EntityIndex index;
    auto entityId1 = index.addEntityId();
    auto entityId2 = index.addEntityId();

    ASSERT_NE(entityId1, entityId2);

    index.addComponent(entityId1, std::pair(1, 1));
    index.addComponent(entityId2, std::pair(3, 4));
    index.addComponent(entityId2, std::pair(3, 8));

    ASSERT_EQ(index.getComponents(entityId1).size(), 1);
    ASSERT_EQ(index.getComponents(entityId2).size(), 2);
}

TEST(TEST_SUITE, UseIndexIdFilter) {
    EntityIndex index;
    auto entityId = index.addEntityId();
    auto filter = index.filterEntityId(entityId);

    ics::ComponentSet compSet;
    // These will be added to the entity
    compSet.emplace(1, 2);
    compSet.emplace(1, 5);
    compSet.emplace(2, 13);
    // These will not be added to the entity
    compSet.emplace(2, 3);
    compSet.emplace(3, 7);

    auto filteredSet = filter(compSet);
    // None of the components match because no component was assigned an entity
    ASSERT_EQ(filteredSet.size(), 0);

    index.addComponent(entityId, std::pair(1, 2));
    index.addComponent(entityId, std::pair(1, 5));
    index.addComponent(entityId, std::pair(2, 13));

    filteredSet = filter(compSet);
    ASSERT_EQ(filteredSet.size(), 3);

    int cumProd = 1;
    for (auto pair : filteredSet) {
        cumProd *= pair.second;
    }

    ASSERT_EQ(cumProd, 130);
}
