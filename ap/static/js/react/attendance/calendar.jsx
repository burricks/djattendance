  /** @jsx React.DOM */

  var ATTENDANCE_STATUS_LOOKUP = {
    P: 'present',
    A: 'absent',
    T: 'tardy',
    U: 'uniform',
    L: 'left-class'
  };

  var SLIP_STATUS_LOOKUP = {
    'A': 'approved',
    'P': 'pending',
    'F': 'fellowship',
    'D': 'denied',
    'S': 'approved'
  };

  var joinValidClasses = function(classes) {
    return _.compact(classes).join(' ');
  };

  var WeekBar = React.createBackboneClass({
    nextWeek: function() {
      this.props.onUserInput('next');
    },
    prevWeek: function() {
      this.props.onUserInput('prev');
    },
    render: function() {
      var startdate = this.props.date.weekday(0).format('M/D/YY');
      var enddate = this.props.date.weekday(6).format('M/D/YY');
      return (
        <div className="btn-toolbar" role="toolbar">
          <div className="controls btn-group">
            <button className="btn btn-info"><span className="glyphicon glyphicon-calendar"></span></button>
          </div>
          <div className="controls btn-group">
            <button className="btn btn-default clndr-previous-button" onClick={this.prevWeek}>Prev</button>
            <div className="daterange btn btn-default disabled">
              {startdate} to {enddate}
            </div>
            <button className="btn btn-default clndr-next-button" onClick={this.nextWeek}>Next</button>
          </div>
        </div>
      );
    }
  });

  var DaysRow = React.createBackboneClass({
    render: function() {
      var days = [];
      for(var i = 0; i < 7; i++) {
        var name = this.props.date.day(i).format('ddd');
        var num = this.props.date.day(i).format('M/D');
        var isToday = this.props.date.day(i).isSame(moment(), 'day');
        var today = isToday ? 'today' : '';
        var classes = joinValidClasses(['schedule-header', today]);
        days.push(
          <div className="col-md-1 no-padding">
            <div className={classes}>
              {name} <br />
              {num}
            </div>
          </div>
        );
      }
      return (
        <div>
          <div className="col-md-1">
            <div className="col-md-1 no-padding">
              <div className="schedule-header dead-space"></div>
            </div>
          </div>
          {days}
        </div>
      );
    }
  });


  var EventView = React.createBackboneClass({
    selectToggle: function() {
      var ev = this.props.event;
      if (ev.id === 'TODAY') {
        return false;
      }
      this.props.selectEvent(ev);
      // Add event to selected list
        // this.props.onUserInput(
        //     this.props.event.id
        // );
    },
    render: function() {
      console.log('render event', this.props.event.attributes.start);
      var ev = this.props.event;
      var roll = this.props.rolls.get(ev.get('roll'));
      var status = roll ? ATTENDANCE_STATUS_LOOKUP[roll.get('status')] : '';
      var todayClass = (ev.id === 'TODAY') ? 'today-marker' : '';
      var leaveslip = this.props.slips.get(ev.get('slip'));
      var slipStatus = leaveslip ? leaveslip.get('status') : '';
      var classes = joinValidClasses(['schedule-event', status, SLIP_STATUS_LOOKUP[slipStatus], todayClass, ev.get('selected')]);
      //ev.get('rolls').at(ev.get('rolls').length - 1).get('roll')
      var divStyle = {
        top: moment.duration(moment(ev.get('start')).format('H:m')).subtract(6, 'hours').asMinutes()/2,
        height: moment(ev.get('end')).diff(moment(ev.get('start')), 'minutes')/2
      };
      return(
        <div className={classes} onClick={this.selectToggle} style={divStyle} data-id={ev.get('id')} data-roll={ev.get('roll_id')}>
          {ev.get('code')}
          <div className="slip-event-status">{SLIP_STATUS_LOOKUP[slipStatus]}</div>
        </div>
      );
    }
  });

  var EventGrid = React.createBackboneClass({
    render: function() {
      var cols = [],
          weekStart = moment(this.props.date).startOf('week'),
          weekEnd = moment(this.props.date).endOf('week'),
          now = moment();
      //get events only from the state's week
      var week_events = this.props.events.filter(function(ev) {
        return (weekStart < moment(ev.get('start')) && weekEnd > moment(ev.get('end')));
      }, this);

      // If today is within current week, add the event marker
      if (weekStart < now && weekEnd > now) {
        var todayEventMarker = new Event({
          id: 'TODAY',
          selected: '',
          start: moment(),
          end: moment()
        });

        week_events.push(todayEventMarker);
      }

      if(this.isMounted()) {
        this.props.setWeekEvents(week_events);
      }

      console.log(week_events, this.props.events.models);

      for(var i = 0; i < 7; i++) {
        //get events for one day
        var day_events = _.filter(week_events, function(ev) {
          return moment(ev.get('start')).weekday() === i; // this == i
        });

        var day_col = [];
        day_events.forEach(function(event) {
          day_col.push(<EventView event={event} slips={this.props.slips} rolls={this.props.rolls} selectEvent={this.props.selectEvent} key={event.id} />);
        }, this);

        var isToday = this.props.date.day(i).isSame(now, 'day');
        var today = isToday ? 'today' : '';
        var classes = joinValidClasses(['day event-col col-md-1 no-padding', today]);
        cols.push(<div key={i} className={classes}>{day_col}</div>);
      }
      return (
        <div>
          {cols}
        </div>
      );
    }
  });


  var Time = React.createBackboneClass({
    render: function() {
      var hour = moment().hour(this.props.hour).format('h A');
      return(
        <div className="hour">
          <div className="hour-text">{hour}</div>
        </div>
      );
    }
  });

  var TimesColumn = React.createBackboneClass({
    render: function() {
      var times = [];
      for(var i = 6; i < 24; i++) {
        times.push(<Time hour={i} />);
      }
      return (
        <div className="col-md-1 timebar">
          {times}
        </div>
      );
    }
  });

  var Leaveslip = React.createBackboneClass({
    getInitialState:function(){
        return {
          type: '',
          comments: '',
          description: '',
          texted: false,
          informed: false
        }
    },
    render: function() {
      var slip = this.props.slip,
          comments = slip.get('comments'),
          comments = (comments && comments !== '') ? comments : (<i>No Comments</i>),
          description = slip.get('description'),
          description = (description && description !== '') ? description : (<i>No Description</i>),
          status = SLIP_STATUS_LOOKUP[slip.get('status')],
          titleClasses = joinValidClasses(['list-group-item active', status]);
      return (
        <div className="leaveslip-container">
          <div className="list-group">
            <a href="#" className={titleClasses}>
              {slip.get('type')}
              <span className="badge">{status}</span>
            </a>
            <div className="list-group-item">{description}</div>
            <div className="list-group-item">{comments}</div>
          </div>
        </div>
      );
    }
  });

  var Leaveslips = React.createBackboneClass({
    render: function() {
      var selectedSlips = this.props.selectedSlips,
          slips = [],
          i, _len;

      for (i = 0, _len = this.props.selectedSlips.length; i < _len; i++) {
        slips.push(<Leaveslip slip={selectedSlips[i]} />);
      }

      if (slips.length === 0) {
        slips = (
          <div>
            <i>No event(s) with leaveslip(s) selected</i>
            <div className="form-group center-padded">
              <button className="btn btn-primary"><span className="glyphicon glyphicon-pencil"></span> Write New Leaveslip</button>
            </div>
          </div>
        );
      }

      console.log('selected slips', selectedSlips);
      return (
        <div className="panel panel-default" id="submit-leaveslip">
          <div className="panel-heading">
            <h3 className="panel-title" id="event-title">Leave Slip(s)</h3>
          </div>
          <div className="panel-body event-info leaveslip-info">
            {slips}
          </div>
        </div>
      );
    }
  });

  var RollView = React.createBackboneClass({
    setRoll: function(ev) {
      console.log('setRoll', arguments, this);
      var btn = ev.target;
      var status = (btn.id.charAt(0)).toUpperCase();
      this.props.setRollStatus(status);

      if (btn.id === 'present') {
        console.log('present');
      } else if (btn.id === 'absent') {
        console.log('absent');
      } else if (btn.id === 'tardy') {
        console.log('tardy');
      } else if (btn.id === 'uniform') {
        console.log('uniform');
      } else if (btn.id === 'left-class') {
        console.log('left-class');
      } else {
        console.log('not recognized button');
      }
    },
    render: function() {
      var disabled = _.size(this.props.selectedEvents) <= 0,
          rollPane;

      if (!disabled) {
        rollPane = (
          <div>
            <button id="present" type="button" onClick={this.setRoll} className="btn btn-default btn-block" disabled={disabled}>Present</button>
            <button id="absent" type="button" onClick={this.setRoll} className="btn btn-danger btn-block" disabled={disabled}>Absent</button>
            <button id="tardy" type="button" onClick={this.setRoll} className="btn btn-warning btn-block" disabled={disabled}>Tardy</button>
            <button id="uniform" type="button" onClick={this.setRoll} className="btn btn-warning btn-block" disabled={disabled}>Uniform</button>
            <button id="left-class" type="button" onClick={this.setRoll} className="btn btn-warning btn-block" disabled={disabled}>Left Class</button>
          </div>
        );
      } else {
        rollPane = (
          <span className="info-message">Please select event(s) to record attendance</span>
        );
      }

      return (
        <div className="panel panel-default" id="submit-roll">
          <div className="panel-heading">
            <h3 className="panel-title" id="event-title">Submit Roll</h3>
          </div>
          <div className="panel-body event-info">
            {rollPane}
          </div>
        </div>
      );
    }
  });

  // working on viewing the leaveslips *not working*

  // var slipsBar = React.createBackboneClass({
  //   render: function() {
  //     var selectedSlips = this.props.selectedSlips,
  //         slips = [],
  //         i, _len;

  //     for (i = 0, _len = this.props.selectedSlips.length; i < _len; i++) {
  //       slips.push(<Leaveslip slip={selectedSlips[i]} />);
  //     }

  //     if (slips.length === 0) {
  //       slips = (
  //         <div>
  //           <i>No event(s) with leaveslip(s) selected</i>
  //           <div className="form-group center-padded">
  //             <button className="btn btn-primary"><span className="glyphicon glyphicon-pencil"></span> Write New Leaveslip</button>
  //           </div>
  //         </div>
  //       );
  //     }
  //     return (
  //       <div className="panel panel-default leaveslip-container">
  //         <div className="list-group">
  //           <a href="#" className={titleClasses}>
  //             {slip.get('type')}
  //             <span className="badge">{status}</span>
  //           </a>
  //           <div className="list-group-item">{description}</div>
  //           <div className="list-group-item">{comments}</div>
  //         </div>
  //       </div>
  //     );
  //   }
  // });

  var Attendance = React.createBackboneClass({
    mixins: [
        // when the view is instantiated,
        // 'events' can be passed as props
        React.BackboneMixin('events'),
        React.BackboneMixin('rolls'),
        React.BackboneMixin('slips')
    ],
    getInitialState: function() {
      return {
        date: moment(),
        selectedEvents: {},
        selectedSlips: [],
        weekEvents: []
      };
    },
    setWeekEvents: function(week_events) {
      this.setState({
        weekEvents: week_events
      });
    },
    handleDate: function(input) {
      var delta = (input === 'prev') ? -7 : 7;
      this.setState({
        date: this.state.date.add('d', delta)
      });
    },
    addSelectedEvent: function(ev) {
      // Add remove selected events based on toggle
      if (!(ev.id in this.state.selectedEvents)) {
        ev.set('selected', 'selected-event');
        this.state.selectedEvents[ev.id] = ev;
      } else {
        ev.set('selected', '');
        delete this.state.selectedEvents[ev.id];
      }
      this.setState({
        selectedEvents: this.state.selectedEvents
      });

      // Add slips selected as well
      this.calculateSelectedSlip();
    },
    getSlipsFromEvents: function(events) {
      var slips = [],
          slipsTable = {},
          eid, ev, slip, sid;
      for (eid in events) {
        ev = events[eid];
        sid = ev.get('slip');
        slip = sid ? this.props.slips.get(sid) : undefined;
        // Only add if unique
        if (slip && !(sid in slipsTable)) {
          slips.push(slip);
          slipsTable[sid] = true;
        }
      }

      return slips;
    },
    getSelectedWeekSlips: function() {
      return getSlipsFromEvents(this.state.weekEvents);
    },
    calculateSelectedSlip: function() {
      // Loop through selected events and push into slips hash table
      var slips = this.getSlipsFromEvents(this.state.selectedEvents);

      console.log('slips calculation', slips, this.state.selectedEvents);
      console.log('slips', slips);
      // Only set selected slip if it's one and only one slip selected
      if (_.size(slips) > 0) {
        this.setState({
          selectedSlips: slips
        });
      } else {
        this.setState({
          selectedSlips: []
        });
      }
    },
    setRollStatus: function(status) {
      if (_.size(this.state.selectedEvents) <= 0) {
        alert('Please select at 1 event before updating the status');
        return false;
      }
      var key, roll, ev,
          updatedRoll = [];
      var traineeID = parseInt($("input#id_trainee").val());
      // Loop through all the selected events and assign status "status"
      for (key in this.state.selectedEvents) {
        ev = this.state.selectedEvents[key];
        roll = this.props.rolls.get(ev.get('roll'));
        if (!roll) {
          roll = new Roll({
            status: status,
            trainee: traineeID,
            monitor: traineeID,
            event: ev.id
          });
          roll.save();
          this.props.rolls.push(roll);
        } else {
          roll.set('status', status);
          updatedRoll.push(_.pick(roll.attributes, 'id', 'status'));
        }
      }

      // empty selectedEvents
      for (key in this.state.selectedEvents) {
        ev = this.state.selectedEvents[key];
        ev.set('selected', '');
      }

      // unselect all the events
      this.setState({
        selectedEvents: {}
      });

      if (updatedRoll.length > 0) {
        this.props.rolls.sync('patch', new Rolls(updatedRoll), {
          success: function(response, status) {
            console.log('updated status to', status);
          }
        });
      }

    },
    render: function() {
      console.log('render attendance');
      return (
      <div>
        <div>
          <WeekBar
            date={this.state.date}
            onUserInput={this.handleDate}
          />
          <hr />
          <div className="row">
            <DaysRow date={this.state.date} />
          </div>
          <div className="row">
            <TimesColumn />
            <EventGrid
              events={this.props.events}
              rolls={this.props.rolls}
              slips={this.props.slips}
              date={this.state.date}
              selectEvent={this.addSelectedEvent}
              setWeekEvents={this.setWeekEvents}
            />
            <div className="col-md-4 action-col">
              <RollView
                setRollStatus={this.setRollStatus}
                selectedEvents={this.state.selectedEvents}
              />
              <Leaveslips
                selectedSlips={this.state.selectedSlips}
              />
            </div>
          </div>
        </div>
        <hr />
      </div>
      );
    }
  });

var attendance = Attendance({events: events, rolls: rolls, slips: slips});

console.log('About to render react.js...');

React.renderComponent(attendance, document.getElementById('react'));

























