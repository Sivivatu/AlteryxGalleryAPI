
def test_workflows_migratable(api_admin_con):
    response = api_admin_con.get_workflows_migratable()[0]
    assert response.status_code == 200


def test_post_workflow(api_admin_con):
    response = api_admin_con.post_workflows_migratable()[0]
    assert response.status_code == 200
