from dataox.resource import oxpoints, account, agent, vacancy


from humfrey.linkeddata.resource import base_resource_registry, ResourceRegistry

resource_registry = base_resource_registry + ResourceRegistry(
    (oxpoints.CollegeHall, 'oxp:College', 'oxp:Hall'),
    oxpoints.Organization,
    (oxpoints.Place, 'oxp:Building', 'oxp:Site', 'oxp:Space', 'oxp:Room'),
    (account.Account, 'foaf:OnlineAccount'),
    (agent.Agent, 'foaf:Agent', 'foaf:Person'),
    vacancy.Vacancy,
)
