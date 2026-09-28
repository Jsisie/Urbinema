import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CollectionFollowRulesTest {
    @Test
    fun `ten in-progress collections is the cap`() {
        assertFalse(CollectionFollowRules.atFollowLimit(9))
        assertTrue(CollectionFollowRules.atFollowLimit(10))
        assertEquals(10, CollectionFollowRules.MAX_IN_PROGRESS_COLLECTIONS)
    }
}
