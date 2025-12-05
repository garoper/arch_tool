from arch_tool.node import Node
from typing import Any, Dict, Iterable, Optional

class Person(Node):
    """A person node in the architecture diagram."""

    def __init__(self,  id: str,
        name: str,
        email: str = "",
        orgUnit: str = "",
        jobTitle: str = "",
        description: str = "",
        ratings: Optional[Dict[str, int]] = None,
        type: str = "person",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None) -> None:
        """Initialize a Person with a unique identifier.

        Args:
            id: Unique identifier
            name: Full name of the person
            email: Email address of the person
            orgUnit: Organizational unit the person belongs to\
            jobTitle: Role or job title of the person
            description: Detailed description of the person
            ratings: Optional dictionary of ratings associated with the person
            type: Type of the node (default: "person")
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
            tags: Optional iterable of tags associated with the person
        """

        self.__name = name
        self.__org_unit = orgUnit
        self.__jobTitle = jobTitle
        self.__description = description
        if metadata is None:
            metadata = {}
        if email:
            metadata["email"] = email            
        if ratings is not None:
            metadata["ratings"] = ratings
        else: 
            metadata["ratings"] = {}

        Node.__init__(
            self, 
            id=id, 
            name=name,
            type=type, metadata=metadata, children=children, tags=tags, comment=comment)
        
    @property
    def title(self) -> str:
        """Get the title for the node."""

        name = self.__name or "N.N."
        title = f"{name} ({self.__jobTitle})" if self.__jobTitle else f"{name}"

        if self.jobTitle:
            title += f"\n{self.__jobTitle}"

        return title

    @property
    def name(self) -> str:
        """Get the full name of the person."""
        return self.__name
    
    @property
    def email(self) -> str:
        """Get the email address of the person."""
        return self.metadata.get("email", "")
    
    @property
    def orgUnit(self) -> str:
        """Get the organizational unit of the person."""
        return self.__org_unit
    
    @property
    def jobTitle(self) -> str:
        """Get the job title of the person."""
        return self.__jobTitle
    
    @property
    def description(self) -> str:
        """Get the description of the person."""
        return self.__description

    def set_description(self, description: str) -> None:
        """Set the description of the person."""
        self.__description = description

    def set_job_title(self, jobTitle: str) -> None:
        """Set the job title of the person."""
        self.__jobTitle = jobTitle

    def set_org_unit(self, org_unit: str) -> None:
        """Set the organizational unit of the person."""
        self.__org_unit = org_unit

    def set_email(self, email: str) -> None:
        """Set the email address of the person."""
        self.metadata["email"] = email

    @property
    def ratings(self) -> Dict[str, int]:
        """Get the ratings associated with the person."""
        return self.metadata.get("ratings", {})

    def set_ratings(self, ratings: Dict[str, int]) -> None:
        """Set the ratings associated with the person."""
        self.metadata["ratings"] = ratings

Node.register_type("person", Person)