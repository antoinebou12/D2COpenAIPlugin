"""
Templates and examples for various diagram formats supported by Kroki.
"""

class DiagramExamples:
    """
    Provides complete examples for different diagram formats supported by Kroki.
    """
    
    @staticmethod
    def get_example(diagram_type: str) -> str:
        """
        Get a comprehensive example for the specified diagram type.
        
        Args:
            diagram_type: The type of diagram (plantuml, mermaid, etc.)
            
        Returns:
            A comprehensive example for the diagram type
        """
        examples = {
            # PlantUML example with more detailed sequence diagram
            "plantuml": """@startuml
skinparam ranksep 20
skinparam dpi 125
skinparam packageTitleAlignment left
rectangle "Main" {
  (main.view)
  (singleton)
}
rectangle "Base" {
  (base.component)
  (component)
  (model)
}
rectangle "<b>main.ts</b>" as main_ts
(component) ..> (base.component)
main_ts ==> (main.view)
(main.view) --> (component)
(main.view) ...> (singleton)
(singleton) ---> (model)
@enduml""",
            
            # Mermaid example with sequence diagram
            "mermaid": """sequenceDiagram
    participant Browser
    participant Webserver
    participant Processor
    
    Browser->>Webserver: GET /diagram/svg/base64
    Webserver->>Processor: Convert text to image
    Processor-->>Webserver: Return image
    Webserver-->>Browser: Deliver SVG image
    
    note over Browser,Webserver: HTTP Request
    note over Webserver,Processor: Internal Processing""",
            
            # BlockDiag example
            "blockdiag": """blockdiag {
  Kroki -> generates -> "Block diagrams";
  Kroki -> is -> "very easy!";
  Kroki [color = "greenyellow"];
  "Block diagrams" [color = "pink"];
  "very easy!" [color = "orange"];
}""",
            
            # SeqDiag example
            "seqdiag": """seqdiag {
  browser  -> webserver [label = "GET /seqdiag/svg/base64"];
  webserver  -> processor [label = "Convert text to image"];
  webserver <-- processor;
  browser <-- webserver;
}""",
            
            # ActDiag example
            "actdiag": """actdiag {
  write -> convert -> image
  lane user {
    label = "User"
    write [label = "Writing text"];
    image [label = "Get diagram image"];
  }
  lane Kroki {
    convert [label = "Convert text to image"];
  }
}""",
            
            # NwDiag example
            "nwdiag": """nwdiag {
  network dmz {
    address = "210.x.x.x/24"
    web01 [address = "210.x.x.1"];
    web02 [address = "210.x.x.2"];
  }
  network internal {
    address = "172.x.x.x/24";
    web01 [address = "172.x.x.1"];
    web02 [address = "172.x.x.2"];
    db01;
    db02;
  }
}""",
            
            # PacketDiag example
            "packetdiag": """packetdiag {
  colwidth = 32;
  node_height = 72;
  0-15: Source Port;
  16-31: Destination Port;
  32-63: Sequence Number;
  64-95: Acknowledgment Number;
  96-99: Data Offset;
  100-105: Reserved;
  106: URG [rotate = 270];
  107: ACK [rotate = 270];
  108: PSH [rotate = 270];
  109: RST [rotate = 270];
  110: SYN [rotate = 270];
  111: FIN [rotate = 270];
  112-127: Window;
  128-143: Checksum;
  144-159: Urgent Pointer;
  160-191: (Options and Padding);
  192-223: data [colheight = 3];
}""",
            
            # RackDiag example
            "rackdiag": """rackdiag {
  16U;
  1: UPS [2U];
  3: DB Server;
  4: Web Server;
  5: Web Server;
  6: Web Server;
  7: Load Balancer;
  8: L3 Switch;
}""",
            
            # C4 diagram (PlantUML extension) example
            "c4plantuml": """!include <C4/C4_Context>
title System Context diagram for Internet Banking System
Person(customer, "Banking Customer", "A customer of the bank, with personal bank accounts.")
System(banking_system, "Internet Banking System", "Allows customers to check their accounts.")
System_Ext(mail_system, "E-mail system", "The internal Microsoft Exchange e-mail system.")
System_Ext(mainframe, "Mainframe Banking System", "Stores all of the core banking information.")
Rel(customer, banking_system, "Uses")
Rel_Back(customer, mail_system, "Sends e-mails to")
Rel_Neighbor(banking_system, mail_system, "Sends e-mails", "SMTP")
Rel(banking_system, mainframe, "Uses")""",
            
            # Bytefield example
            "bytefield": """(defattrs :bg-green {:fill "#a0ffa0"})
(defattrs :bg-yellow {:fill "#ffffa0"})
(defattrs :bg-pink {:fill "#ffb0a0"})
(defattrs :bg-cyan {:fill "#a0fafa"})
(defattrs :bg-purple {:fill "#e4b5f7"})
(defn draw-group-label-header
  [span label]
  (draw-box (text label [:math {:font-size 12}]) {:span span :borders #{} :height 14}))
(defn draw-remotedb-header
  [kind args]
  (draw-column-headers)
  (draw-group-label-header 5 "start")
  (draw-group-label-header 5 "TxID")
  (draw-group-label-header 3 "type")
  (draw-group-label-header 2 "args")
  (draw-group-label-header 1 "tags")
  (next-row 18)
  (draw-box 0x11 :bg-green)
  (draw-box 0x872349ae [{:span 4} :bg-green])
  (draw-box 0x11 :bg-yellow)
  (draw-box (text "TxID" :math) [{:span 4} :bg-yellow])
  (draw-box 0x10 :bg-pink)
  (draw-box (hex-text kind 4 :bold) [{:span 2} :bg-pink])
  (draw-box 0x0f :bg-cyan)
  (draw-box (hex-text args 2 :bold) :bg-cyan)
  (draw-box 0x14 :bg-purple)
  (draw-box (text "0000000c" :hex [[:plain {:font-weight "light" :font-size 16}] " (12)"]) [{:span 4} :bg-purple])
  (draw-box (hex-text 6 2 :bold) [:box-first :bg-purple])
  (doseq [val [6 6 3 6 6 6 6 3]]
    (draw-box (hex-text val 2 :bold) [:box-related :bg-purple]))
  (doseq [val [0 0]]
    (draw-box val [:box-related :bg-purple]))
  (draw-box 0 [:box-last :bg-purple]))
(draw-remotedb-header 0x4702 9)"""
        }
        
        # Get the example or return a message if not found
        return examples.get(diagram_type.lower(), 
                          "# No specific example available for this diagram type.\n"
                          "# Please refer to the documentation for " + diagram_type)

class DiagramTemplates:
    """
    Provides starter templates for different diagram formats.
    """
    
    @staticmethod
    def get_template(diagram_type: str) -> str:
        """
        Get a starter template for the specified diagram type.
        
        Args:
            diagram_type: The type of diagram (plantuml, mermaid, etc.)
            
        Returns:
            A starter template for the diagram type
        """
        templates = {
            # Basic sequence diagram for PlantUML
            "plantuml": """@startuml
participant User
participant System

User -> System: Request
System --> User: Response
@enduml""",
            
            # Basic sequence diagram for Mermaid
            "mermaid": """sequenceDiagram
    participant User
    participant System
    
    User->>System: Request
    System-->>User: Response""",
            
            # Basic diagram for D2
            "d2": """User -> System: Request
System -> User: Response""",
            
            # Basic diagram for Graphviz
            "graphviz": """digraph G {
    User -> System [label="Request"];
    System -> User [label="Response"];
}""",
            
            # Basic diagram for BlockDiag
            "blockdiag": """blockdiag {
  User -> System -> Database;
  System -> User;
}""",
            
            # Basic diagram for BPMN
            "bpmn": """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1"/>
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="173" y="102" width="36" height="36"/>
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>""",
            
            # Basic diagram for ERD
            "erd": """[Person]
*name
height
weight""",
            
            # Basic diagram for Bytefield
            "bytefield": """(defattrs :bg-green {:fill "#a0ffa0"})
(defattrs :bg-yellow {:fill "#ffffa0"})
(defattrs :bg-pink {:fill "#ffb0a0"})
(defattrs :bg-cyan {:fill "#a0fafa"})
(defattrs :bg-purple {:fill "#e4b5f7"})

(def row-height 40)
(def row-header-width 50)
(def box-width 30)

(defn draw-packet-header
  []
  (draw-column-headers)
  (draw-box 0 0 8)
  (draw-box 0 1 8)
  (draw-gap "Payload")
  (draw-bottom))

(draw-packet-header)""",
        }
        
        # Try to get a specific template, fall back to a generic one
        return templates.get(diagram_type.lower(), 
                           "# No specific template available for this diagram type.\n"
                           "# Please refer to the documentation for this diagram type.")

# Example usage:
def demo():
    # Get and print a template for Mermaid
    mermaid_template = DiagramTemplates.get_template("mermaid")
    print("MERMAID TEMPLATE:")
    print(mermaid_template)
    print("\n")
    
    # Get and print a comprehensive example for Mermaid
    mermaid_example = DiagramExamples.get_example("mermaid")
    print("MERMAID EXAMPLE:")
    print(mermaid_example)

if __name__ == "__main__":
    demo()